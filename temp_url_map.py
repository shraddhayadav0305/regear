from app import app
for rule in app.url_map.iter_rules():
    if 'admin' in rule.rule or 'dashboard' in rule.rule:
        print(rule.endpoint, rule.rule)
