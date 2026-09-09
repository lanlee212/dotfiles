#!/usr/bin/env python3
import json
import time
from libqtile.command.client import InteractiveCommandClient

def main():
    c = InteractiveCommandClient()
    last_state = None
    
    while True:
        try:
            # Ask Qtile for group data
            groups = c.get_groups()
            current_group = c.group.info()["name"]
            
            state = []
            for name, info in groups.items():
                # Skip the scratchpad group
                if name.lower() == "scratchpad":
                    continue
                    
                state.append({
                    "name": name,
                    "active": name == current_group,
                    "occupied": len(info.get("windows", [])) > 0
                })
            
            # Convert to JSON and only print if the state has changed
            state_json = json.dumps(state)
            if state_json != last_state:
                print(state_json, flush=True)
                last_state = state_json
                
        except Exception as e:
            print(f"Error: {e}", flush=True)
            
        time.sleep(0.2)

if __name__ == "__main__":
    main()
