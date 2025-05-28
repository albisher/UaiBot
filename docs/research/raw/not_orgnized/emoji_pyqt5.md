## Emoji Support in PyQt5

**PyQt5** does not ship with a built-in emoji picker or a dedicated emoji widget, but it fully supports Unicode, which means you can display any emoji supported by the Unicode standard in text-based widgets (like `QLabel`, `QTextEdit`, or `QLineEdit`) as long as the system font supports emoji rendering[2][1]. 

### How to Use Emojis in PyQt5

- **Direct Unicode Input**: You can directly insert emoji characters (e.g., 😃) into your widget text strings. This works if the font used by the widget supports color emoji glyphs[2][1].
- **Set Emoji-Compatible Font**: To ensure emojis display correctly, set a font that supports color emojis, such as "Segoe UI Emoji" (Windows), "Noto Color Emoji" (Linux), or "Apple Color Emoji" (macOS)[2][1].

```python
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QFont

app = QApplication([])
label = QLabel("Hello 😃")
label.setFont(QFont("Segoe UI Emoji", 20))  # Use a font that supports emojis
label.show()
app.exec_()
```

- **Emoji List**: The full range of Unicode emoji is available. You can find a complete list of emoji codes and their Unicode representations in resources like the [emojis-list GitHub repository][3] or by using the `emoji` Python package[7].

### Emoji Input Methods

- **Manual Input**: Users can paste emoji characters into text fields if their OS supports emoji input.
- **Virtual Keyboard**: For a custom emoji picker, you can create a floating widget (e.g., a `QTableView` with emoji icons) that inserts the selected emoji into your text widget[2].

### Using the `emoji` Python Package

You can use the `emoji` package to convert emoji aliases (like `:thumbs_up:`) to emoji characters and vice versa[7]:

```python
import emoji
print(emoji.emojize('Python is :thumbs_up:'))  # Outputs: Python is 👍
```

## Icon Support in PyQt5

### Built-in Qt Icons

PyQt5 provides a set of standard icons accessible via `QStyle` (e.g., for file dialogs, warnings, etc.)[6]:

```python
from PyQt5.QtWidgets import QApplication, QStyle, QPushButton

app = QApplication([])
button = QPushButton()
icon = app.style().standardIcon(QStyle.SP_MessageBoxInformation)
button.setIcon(icon)
button.show()
app.exec_()
```

- These icons cover common UI actions (open, save, warning, etc.) and are platform-independent[6].

### Additional Icon Sets

- **Fugue Icons**: A free, extensive icon set recommended for PyQt5 applications[6].
- **System Icons**: On Linux, you can access system theme icons using `QIcon.fromTheme()`[6].

### Example of Available Icons

Some icon names you might find (not exhaustive):

| Icon Name                     | Usage Example                        |
|-------------------------------|--------------------------------------|
| SP_MessageBoxCritical         | Critical error dialogs               |
| SP_MessageBoxInformation      | Information dialogs                  |
| SP_DirOpenIcon                | Open directory button                |
| SP_FileIcon                   | Generic file icon                    |

## Summary Table: Emoji vs. Qt Icons

| Feature        | Emoji                              | Qt Built-in Icons                  |
|----------------|------------------------------------|------------------------------------|
| Source         | Unicode standard                    | Qt's `QStyle`                      |
| Use in PyQt5   | Any text widget with emoji font     | Any widget supporting icons        |
| Customization  | Font-dependent, Unicode-based       | Limited to available icon set      |
| Input Method   | Paste, type, or custom picker       | Set via `setIcon()`                |

## References for Emoji Lists

- Unicode emoji list: [emojis-list GitHub][3]
- Python emoji package: [emoji on PyPI][7]

---

**In summary:**  
PyQt5 supports all Unicode emojis if you use a compatible font, and you can use the standard set of Qt icons for common UI elements. For emoji input or display, ensure the font supports color emojis, and consider the `emoji` package for easy conversion between codes and characters[2][7][6].

Citations:
[1] https://stackoverflow.com/questions/66609707/how-to-display-emojis-in-pyqt5
[2] https://forum.qt.io/topic/77986/emoji-support
[3] https://github.com/Kikobeats/emojis-list
[4] https://www.pythonguis.com/tutorials/pyqt-basic-widgets/
[5] https://k3a.me/telegram-emoji-list-codes-descriptions/
[6] https://www.pythonguis.com/faq/built-in-qicons-pyqt/
[7] https://pypi.org/project/emoji/
[8] https://gist.github.com/ostr00000/30c9e732550baa0c13a73fd3320e7d55

---
Answer from Perplexity: pplx.ai/share