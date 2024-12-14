import yaml

to_yaml = {'token' : "TOKEN",
            'admin_pass' : "PASSWORD"}
with open('config.yaml', 'w') as f:
    yaml.dump(to_yaml, f)

with open('config.yaml') as f:
    print(f.read())