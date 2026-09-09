import subprocess
import json
import os
import datetime
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PLAYERS_FILE = os.path.join(DATA_DIR, "players.csv")
ALERTS_FILE = os.path.join(DATA_DIR, "live_news_alerts.json")

MANUAL_CRITICAL_STATUSES = {
    'tyreek hill': {
        'injury_risk': 'OUT',
        'status_label': 'OUT (Season/FA)',
        'notes': 'OUT - Severe knee injury dislocation/ACL, unsigned free agent. Do not draft.',
        'base_points_override': 0.0
    },
    't.j. hockenson': {
        'injury_risk': 'PUP',
        'status_label': 'PUP (ACL)',
        'notes': 'Starting season on PUP (recovering from ACL); target return mid-season.',
        'base_points_override': None
    },
    'nick chubb': {
        'injury_risk': 'PUP',
        'status_label': 'PUP (Knee)',
        'notes': 'Starting season on PUP (recovering from multi-ligament knee); mid-season return.',
        'base_points_override': None
    },
    'jonathon brooks': {
        'injury_risk': 'PUP',
        'status_label': 'PUP (ACL)',
        'notes': 'Starting on PUP (recovering from ACL); second-half rookie upside.',
        'base_points_override': None
    },
    'hollywood brown': {
        'injury_risk': 'IR',
        'status_label': 'IR (Shoulder)',
        'notes': 'On IR (sternoclavicular shoulder injury); out first 4-8 weeks.',
        'base_points_override': None
    }
}

def fetch_espn_injuries():
    """Fetches real-time injury reports from ESPN's public API."""
    try:
        cmd = ['curl', '-s', '--max-time', '10', 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries']
        res = subprocess.run(cmd, capture_output=True, text=True)
        if not res.stdout or not res.stdout.startswith('{'):
            return {}
        data = json.loads(res.stdout)
        
        espn_injuries = {}
        for team in data.get('injuries', []):
            team_name = team.get('displayName', '')
            for item in team.get('injuries', []):
                ath = item.get('athlete', {})
                name = ath.get('displayName')
                pos = ath.get('position', {}).get('abbreviation')
                typ = item.get('type', {}).get('description', '')
                detail = item.get('details', {})
                fantasy_stat = detail.get('fantasyStatus', {}).get('description', '')
                detail_txt = detail.get('detail') or detail.get('type', '')
                notes_items = item.get('notes', {}).get('items', [])
                headline = notes_items[0].get('headline', '') if notes_items else ''
                
                if name:
                    espn_injuries[name.lower().strip()] = {
                        'name': name,
                        'pos': pos,
                        'team': team_name,
                        'status': typ,
                        'fantasy_status': fantasy_stat,
                        'detail': detail_txt if detail_txt != 'Not Specified' else '',
                        'headline': headline
                    }
        return espn_injuries
    except Exception as e:
        print(f"Error fetching ESPN injuries: {e}")
        return {}

def fetch_espn_news():
    """Fetches breaking NFL news and player mentions from ESPN."""
    try:
        cmd = ['curl', '-s', '--max-time', '10', 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/news']
        res = subprocess.run(cmd, capture_output=True, text=True)
        if not res.stdout or not res.stdout.startswith('{'):
            return []
        data = json.loads(res.stdout)
        
        articles = []
        for art in data.get('articles', []):
            hl = art.get('headline')
            desc = art.get('description')
            pub = art.get('published')
            athletes = [c.get('description') for c in art.get('categories', []) if c.get('type') == 'athlete']
            if hl:
                articles.append({
                    'headline': hl,
                    'description': desc,
                    'athletes': athletes,
                    'published': pub
                })
        return articles
    except Exception as e:
        print(f"Error fetching ESPN news: {e}")
        return []

def sync_injuries_and_news():
    """
    Syncs injuries with data/players.csv and outputs live alert json.
    Returns the alert dict.
    """
    espn_injuries = fetch_espn_injuries()
    espn_news = fetch_espn_news()
    
    if not os.path.exists(PLAYERS_FILE):
        return None
        
    df = pd.read_csv(PLAYERS_FILE)
    
    out_alerts = []
    ir_alerts = []
    questionable_alerts = []
    
    for idx, row in df.iterrows():
        pname_clean = str(row['name']).lower().strip()
        
        # 1. Apply manual critical overrides first
        if pname_clean in MANUAL_CRITICAL_STATUSES:
            override = MANUAL_CRITICAL_STATUSES[pname_clean]
            df.at[idx, 'injury_risk'] = override['injury_risk']
            df.at[idx, 'notes'] = override['notes']
            if override['base_points_override'] is not None:
                df.at[idx, 'base_points'] = override['base_points_override']
                df.at[idx, 'rec'] = 0
                df.at[idx, 'rec_yds'] = 0
                df.at[idx, 'rec_tds'] = 0
                df.at[idx, 'rush_yds'] = 0
                df.at[idx, 'rush_tds'] = 0
                df.at[idx, 'pass_yds'] = 0
                df.at[idx, 'pass_tds'] = 0
            
            if override['injury_risk'] == 'OUT':
                out_alerts.append({
                    'name': row['name'], 'pos': row['pos'], 'team': row['team'],
                    'status': 'OUT', 'note': override['notes']
                })
            elif override['injury_risk'] in ['PUP', 'IR']:
                ir_alerts.append({
                    'name': row['name'], 'pos': row['pos'], 'team': row['team'],
                    'status': override['injury_risk'], 'note': override['notes']
                })
            continue

        # 2. Check ESPN real-time injury report
        if pname_clean in espn_injuries:
            espn_info = espn_injuries[pname_clean]
            raw_status = (espn_info['status'] or '').lower()
            fantasy_stat = (espn_info['fantasy_status'] or '').upper()
            detail = espn_info['detail']
            
            # OUT
            if 'out' in raw_status or fantasy_stat in ['OUT', 'RESERVE-CEL']:
                df.at[idx, 'injury_risk'] = 'OUT'
                note_str = f"OUT - {detail} (ESPN official report)" if detail else "OUT (ESPN official report)"
                df.at[idx, 'notes'] = note_str
                out_alerts.append({
                    'name': row['name'], 'pos': row['pos'], 'team': row['team'],
                    'status': 'OUT', 'note': note_str
                })
                
            # IR (Injured Reserve)
            elif 'injured reserve' in raw_status or fantasy_stat in ['IR', 'IR-R']:
                df.at[idx, 'injury_risk'] = 'IR'
                note_str = f"IR - {detail} (Placed on Injured Reserve)" if detail else "On Injured Reserve (IR)"
                df.at[idx, 'notes'] = note_str
                ir_alerts.append({
                    'name': row['name'], 'pos': row['pos'], 'team': row['team'],
                    'status': 'IR', 'note': note_str
                })
                
            # PUP
            elif 'pup' in raw_status or fantasy_stat in ['PUP', 'PUP-R']:
                df.at[idx, 'injury_risk'] = 'PUP'
                note_str = f"PUP - {detail} (Physically Unable to Perform)" if detail else "Starting on PUP List"
                df.at[idx, 'notes'] = note_str
                ir_alerts.append({
                    'name': row['name'], 'pos': row['pos'], 'team': row['team'],
                    'status': 'PUP', 'note': note_str
                })
                
            # Questionable
            elif 'questionable' in raw_status or fantasy_stat in ['QUESTIONABLE']:
                df.at[idx, 'injury_risk'] = 'Questionable'
                if detail and 'not specified' not in detail.lower():
                    df.at[idx, 'notes'] = f"Q - Dealing with {detail}. Active status monitored."
                questionable_alerts.append({
                    'name': row['name'], 'pos': row['pos'], 'team': row['team'],
                    'status': 'Questionable', 'detail': detail
                })
                
    # Save back to CSV
    df.to_csv(PLAYERS_FILE, index=False)
    
    alert_payload = {
        'last_updated': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'out_count': len(out_alerts),
        'ir_count': len(ir_alerts),
        'out_players': out_alerts,
        'ir_pup_players': ir_alerts,
        'questionable_players': questionable_alerts[:15],
        'breaking_news': espn_news[:6]
    }
    
    try:
        with open(ALERTS_FILE, 'w') as f:
            json.dump(alert_payload, f, indent=2)
    except Exception as e:
        print(f"Error saving alerts file: {e}")
        
    return alert_payload

if __name__ == "__main__":
    alerts = sync_injuries_and_news()
    print("Sync finished successfully!")
    print(f"OUT players: {alerts['out_count']}")
    print(f"IR/PUP players: {alerts['ir_count']}")
    print(f"News stories: {len(alerts['breaking_news'])}")
