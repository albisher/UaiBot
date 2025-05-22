# Safari Browser Automation on Mac

## Open a New Tab with a URL
```zsh
function new_safari_tab() {
  osascript -e "tell application \"Safari\"
    activate
    tell front window
      set current tab to (make new tab with properties {URL:\"$1\"})
    end tell
  end tell"
}
# Usage:
new_safari_tab "https://www.google.com"
```

## Search for a Query
```zsh
search_term="your query here"
encoded_term=$(printf "%s" "$search_term" | jq -sRr @uri)
new_safari_tab "https://www.google.com/search?q=$encoded_term"
```

## Click Elements on the Page (JavaScript Injection)
```zsh
osascript <<EOF
tell application "Safari"
  activate
  tell front document
    do JavaScript "document.getElementById('searchButton').click();"
  end tell
end tell
EOF
```
- Target by ID, class, or tag as needed.

## Track Tabs
```applescript
tell application "Safari"
  set myWindow to front window
  set myTab to current tab of myWindow
  -- Perform actions on myTab
end tell
```

## Full Example Script
```zsh
#!/bin/zsh
# Open Google in a new tab
new_safari_tab "https://www.google.com"
# Search for "example query"
search_term="example query"
encoded_term=$(printf "%s" "$search_term" | jq -sRr @uri)
new_safari_tab "https://www.google.com/search?q=$encoded_term"
# Click the first search result
sleep 2
osascript <<EOF
tell application "Safari"
  activate
  tell front document
    do JavaScript "document.querySelector('h3').click();"
  end tell
end tell
EOF
```

## Tips
- Add `sleep` to allow pages to load before interacting.
- Use JavaScript checks to avoid errors.
- For complex workflows, consider Automator or dedicated scripts. 