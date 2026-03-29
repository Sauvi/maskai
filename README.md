# MaskAI — Mask Sensitive Code Before Sending to AI

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**MaskAI** automatically masks sensitive identifiers in your code before you share it with AI tools like ChatGPT or Claude, then unmasks the AI's response back to your real code.

Perfect for developers working with proprietary code who need AI assistance but must comply with company security policies.

---

## 🎯 Why MaskAI?

**The Problem:**
- Your company's security policy forbids pasting proprietary code into AI tools
- But you need AI help to code faster and solve problems
- Manually replacing names is tedious and error-prone

**The Solution:**
- MaskAI masks all sensitive identifiers (classes, functions, variables, parameters) locally
- Share the masked version with AI tools safely
- Unmask the AI response with one click
- All processing happens locally — nothing leaves your machine

---

## ✨ Features

- 🔒 **100% Local** — All masking happens on your machine. Nothing is sent anywhere.
- 🎯 **Smart Detection** — Automatically detects and masks classes, functions, parameters, and variables
- 🌐 **Multi-Language** — Supports Python, JavaScript, TypeScript, JSX, and TSX
- ⚙️ **Customizable** — Choose what to mask via settings (classes only, skip variables, etc.)
- ⚡ **Fast & Simple** — Right-click to mask, right-click to unmask
- 🗺️ **Mapping Panel** — See exactly what was masked

---

## 🚀 How to Use

### Masking Code

1. **Select code** you want to send to AI (or use "Mask Entire File")
2. **Right-click** → **"MaskAI: Copy Masked Code"**
3. **Masked code is copied to clipboard** and mapping panel appears
4. **Paste into ChatGPT/Claude** safely

![MaskAI Demo](./demo.gif)

### Unmasking AI Response

1. **Get AI response** with masked identifiers
2. **Paste response into your editor**
3. **Select the response** → **Right-click** → **"MaskAI: Unmask and Replace"**
4. **Real names are restored** instantly

---

## 📋 Commands

- **MaskAI: Copy Masked Code** — Mask selected code and copy to clipboard
- **MaskAI: Mask Entire File** — Mask the entire file at once
- **MaskAI: Unmask and Replace** — Unmask selected text in-place

---

## ⚙️ Settings

Customize what gets masked in VS Code settings:

- **Mask Classes** — Mask class names (default: ✅ enabled)
- **Mask Functions** — Mask function and method names (default: ✅ enabled)
- **Mask Parameters** — Mask function parameters (default: ✅ enabled)
- **Mask Variables** — Mask variable names (default: ✅ enabled)

**How to access:**
1. Open Settings (`Ctrl + ,`)
2. Search for "MaskAI"
3. Toggle checkboxes

---

## 🌍 Supported Languages

- ✅ Python (`.py`)
- ✅ JavaScript (`.js`, `.mjs`, `.cjs`)
- ✅ TypeScript (`.ts`)
- ✅ React JSX/TSX (`.jsx`, `.tsx`)

More languages coming soon! Request yours in [Issues](https://github.com/Sauvi/maskai/issues).

---

## 🔐 Privacy & Security

**MaskAI is 100% local:**
- No data is sent to any server
- No telemetry or tracking
- All masking happens on your machine
- Mapping files are stored locally in the extension folder
- You have complete control over your code

**What gets masked:**
- Class names → `Class1`, `Class2`, etc.
- Function/method names → `method1`, `method2`, etc.
- Parameters → `param1`, `param2`, etc.
- Variables → `var1`, `var2`, etc.

**What does NOT get masked:**
- Language keywords (`def`, `class`, `function`, `const`, etc.)
- Built-in functions (`print`, `console.log`, etc.)
- Strings and comments
- Code structure and logic

---

## 📝 Example

**Original Code:**
```python
class PaymentProcessor:
    def calculate_fee(self, amount, tax_rate):
        total_fee = amount * tax_rate
        return total_fee
```

**Masked Code (copied to clipboard):**
```python
class Class1:
    def method1(self, param1, param2):
        var1 = param1 * param2
        return var1
```

**AI can help with the logic without seeing your proprietary names!**

---

## 🛠️ Requirements

- **VS Code** 1.110.0 or higher
- **Python 3.x** installed on your system (for the masking engine)

---

## 📦 Installation

1. Open VS Code
2. Go to Extensions (`Ctrl + Shift + X`)
3. Search for **"MaskAI"**
4. Click **Install**

Or install from [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=saurabh-dev.maskai)

---

## 🐛 Known Limitations

- Multiline function parameters (split across lines) may not be fully detected
- Only supports Python and JavaScript/TypeScript currently
- Mapping is session-based (if you restart VS Code, use the same mapping file)

---

## 🤝 Contributing

Found a bug? Want a feature? 

- 🐛 [Report Issues](https://github.com/Sauvi/maskai/issues)
- 💡 [Request Features](https://github.com/Sauvi/maskai/issues)
- 🔧 [Submit Pull Requests](https://github.com/Sauvi/maskai/pulls)

---

## 📄 License

MIT License - feel free to use, modify, and distribute.

---

## 🙏 Support

If MaskAI helps you, consider:
- ⭐ [Star the repo](https://github.com/Sauvi/maskai)
- 📢 Share with your team
- 💬 Leave a review on the [marketplace](https://marketplace.visualstudio.com/items?itemName=saurabh-dev.maskai)

---

**Made with ❤️ for developers who need AI help without compromising security.**
