import main
import yaml

if __name__ == '__main__':
  print(yaml.dump(main.load(), default_flow_style=False)),
