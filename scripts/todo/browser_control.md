# Browser Control Automation TODO

## Mac Automation
- [x] Normalize browser names for macOS (e.g., 'chrome' -> 'Google Chrome', 'safari' -> 'Safari', etc.)
- [x] Add robust AppleScript for Safari (reuse tab, open new tab, inject JavaScript, click elements)
- [x] Add robust AppleScript for Chrome (reuse tab, open new tab, inject JavaScript, click elements)
- [x] Fallback to open new window/tab for Firefox and other browsers (document Selenium/Playwright for advanced automation)
- [x] Add shell functions/scripts for Safari/Chrome (see scripts/mac/browser_automation_safari.md)

## Cross-Browser Automation
- [x] Integrate Selenium/Playwright automation for Chrome, Firefox, Safari (Python/JS)
- [x] Add CLI examples for Cypress (see docs/automation/cross_browser_automation.md)
- [x] Document best practices for tab/window tracking and element interaction

## Testing & Documentation
- [x] Test all automation methods on macOS
- [x] Test Selenium/Playwright on all supported browsers
- [x] Document usage and troubleshooting
- [x] Reference scripts/mac/browser_automation_safari.md and docs/automation/cross_browser_automation.md

## Next Steps
- [ ] Add support for browser profiles and user data directories
- [ ] Implement browser state persistence between sessions
- [ ] Add support for browser extensions and add-ons
- [ ] Implement browser performance monitoring
- [ ] Add support for browser network interception and modification 