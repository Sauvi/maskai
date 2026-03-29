# masker.py
# MaskAI — Core Masking Engine
# v2.0 — Added JavaScript/TypeScript support

import re
import json
import sys
import argparse

# Fix Windows encoding issue
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# ── BUILTINS BY LANGUAGE ──────────────────────────────

PYTHON_BUILTINS = {
    'print', 'len', 'range', 'int', 'str', 'float',
    'bool', 'list', 'dict', 'set', 'tuple', 'None',
    'True', 'False', 'self', 'cls', 'return', 'if',
    'else', 'elif', 'for', 'while', 'import', 'from',
    'class', 'def', 'pass', 'break', 'continue', 'in',
    'not', 'and', 'or', 'is', 'try', 'except', 'finally',
    'with', 'as', 'raise', 'lambda', 'yield', 'type',
    'super', 'object', 'Exception', 'append', 'extend',
    'keys', 'values', 'items', 'get', 'open', 'read',
    'write', 'close', 'format', 'split', 'join', 'strip',
    'input', 'output', 'result', 'data', 'value', 'name',
    'index', 'count', 'total', 'size', 'key', 'val',
    'error', 'message', 'response', 'request', 'status',
    'i', 'j', 'k', 'x', 'y', 'z', 'n', 'e'
}

JS_BUILTINS = {
    # Core JavaScript keywords
    'console', 'window', 'document', 'setTimeout', 'setInterval',
    'clearTimeout', 'clearInterval', 'alert', 'prompt', 'confirm',
    'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'eval',
    # Built-in objects
    'JSON', 'Math', 'Date', 'Array', 'Object', 'String',
    'Number', 'Boolean', 'Function', 'Error', 'TypeError',
    'ReferenceError', 'SyntaxError', 'Promise', 'Map', 'Set',
    'WeakMap', 'WeakSet', 'Proxy', 'Reflect', 'Symbol',
    # Keywords
    'async', 'await', 'fetch', 'then', 'catch', 'finally',
    'resolve', 'reject', 'require', 'exports', 'module',
    'import', 'export', 'default', 'from', 'as', 'class',
    'extends', 'constructor', 'static', 'super', 'this', 'new',
    'typeof', 'instanceof', 'delete', 'void', 'return', 'if',
    'else', 'switch', 'case', 'for', 'while', 'do', 'break',
    'continue', 'try', 'throw', 'const', 'let', 'var', 'function',
    # Literals
    'true', 'false', 'null', 'undefined', 'NaN', 'Infinity',
    # Common built-in properties/methods
    'arguments', 'length', 'push', 'pop', 'shift', 'unshift',
    'slice', 'splice', 'map', 'filter', 'reduce', 'forEach',
    'find', 'findIndex', 'some', 'every', 'includes', 'join',
    'split', 'replace', 'match', 'search', 'indexOf', 'lastIndexOf',
    'keys', 'values', 'entries', 'hasOwnProperty', 'toString',
    'valueOf', 'toLocaleString', 'hasOwnProperty', 'isPrototypeOf',
    # DOM/Event APIs
    'addEventListener', 'removeEventListener', 'preventDefault',
    'stopPropagation', 'querySelector', 'querySelectorAll',
    'getElementById', 'getElementsByClassName', 'createElement',
    # Common single-letter vars
    'i', 'j', 'k', 'x', 'y', 'z', 'n', 'e', 'err',
    # TypeScript keywords
    'interface', 'type', 'enum', 'namespace', 'declare',
    'abstract', 'implements', 'private', 'protected', 'public',
    'readonly', 'any', 'unknown', 'never', 'void'
}

# ── LANGUAGE DETECTION ────────────────────────────────

def detect_language(code: str, filename: str = None) -> str:
    """
    Detect language from file extension or code patterns
    """
    # Check file extension first
    if filename:
        ext = filename.lower().split('.')[-1]
        if ext == 'py':
            return 'python'
        elif ext in ['js', 'jsx', 'ts', 'tsx', 'mjs', 'cjs']:
            return 'javascript'
    
    # Pattern-based detection as fallback
    if re.search(r'\bdef\s+\w+\s*\(', code) or re.search(r'^\s*import\s+\w+', code, re.MULTILINE):
        return 'python'
    elif re.search(r'\bconst\s+\w+\s*=', code) or re.search(r'\bfunction\s+\w+\s*\(', code):
        return 'javascript'
    
    # Default to Python for backward compatibility
    return 'python'


# ── PYTHON EXTRACTION ─────────────────────────────────

def extract_identifiers_python(code: str) -> list:
    """Extract Python identifiers (original logic)"""
    identifiers = []
    seen = set()

    def add(id_type, name):
        if (name not in PYTHON_BUILTINS and
            name not in seen and
            len(name) > 1 and
            not name.startswith('__')):
            identifiers.append((id_type, name))
            seen.add(name)

    # Class names
    for name in re.findall(r'class\s+([A-Za-z_][A-Za-z0-9_]*)', code):
        add('class', name)

    # Function names
    for name in re.findall(r'def\s+([A-Za-z_][A-Za-z0-9_]*)', code):
        add('function', name)

    # Function parameters
    func_sigs = re.findall(r'def\s+[A-Za-z_][A-Za-z0-9_]*\s*\((.*?)\)', code)
    for sig in func_sigs:
        params = [p.strip().split(':')[0].split('=')[0].strip()
                  for p in sig.split(',')]
        for param in params:
            if param and param != 'self' and param != 'cls':
                add('parameter', param)

    # Variable assignments
    for name in re.findall(r'^[ \t]*([a-z_][a-zA-Z0-9_]*)\s*=',
                           code, re.MULTILINE):
        add('variable', name)

    return identifiers


# ── JAVASCRIPT EXTRACTION ────────────────────────────

def extract_identifiers_javascript(code: str) -> list:
    """Extract JavaScript/TypeScript identifiers"""
    identifiers = []
    seen = set()

    def add(id_type, name):
        if (name not in JS_BUILTINS and
            name not in seen and
            len(name) > 1):
            identifiers.append((id_type, name))
            seen.add(name)

    # Class names
    for name in re.findall(r'class\s+([A-Za-z_$][A-Za-z0-9_$]*)', code):
        add('class', name)

    # Interface names (TypeScript)
    for name in re.findall(r'interface\s+([A-Za-z_$][A-Za-z0-9_$]*)', code):
        add('class', name)

    # Type aliases (TypeScript)
    for name in re.findall(r'type\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=', code):
        add('class', name)

    # Function declarations: function funcName
    for name in re.findall(r'function\s+([A-Za-z_$][A-Za-z0-9_$]*)', code):
        add('function', name)

    # Arrow functions: const funcName = (...) =>
    for name in re.findall(r'(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', code):
        add('function', name)

    # Method definitions in classes: methodName(...) { or async methodName(...) {
    for name in re.findall(r'^\s+(?:async\s+)?([A-Za-z_$][A-Za-z0-9_$]*)\s*\([^)]*\)\s*\{', code, re.MULTILINE):
        if name not in ['constructor', 'if', 'for', 'while', 'switch', 'catch']:
            add('function', name)

    # Function parameters from all function types
    func_sigs = []
    # Regular functions
    func_sigs += re.findall(r'function\s+[A-Za-z_$][A-Za-z0-9_$]*\s*\((.*?)\)', code)
    # Arrow functions
    func_sigs += re.findall(r'(?:const|let|var)\s+[A-Za-z_$][A-Za-z0-9_$]*\s*=\s*(?:async\s*)?\((.*?)\)\s*=>', code)
    # Class methods
    func_sigs += re.findall(r'^\s+(?:async\s+)?[A-Za-z_$][A-Za-z0-9_$]*\s*\((.*?)\)\s*\{', code, re.MULTILINE)
    
    for sig in func_sigs:
        # Split by comma, handle destructuring and defaults
        params = [p.strip().split(':')[0].split('=')[0].strip()
                  for p in sig.split(',')]
        for param in params:
            # Clean up destructuring and rest params
            param = re.sub(r'[{}\[\]...]', '', param).strip()
            if param and not param.startswith('_'):
                add('parameter', param)

    # Variable declarations: const/let/var varName =
    for name in re.findall(r'(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=', code):
        add('variable', name)

    return identifiers


# ── MAIN EXTRACTION ROUTER ───────────────────────────

def extract_identifiers(code: str, language: str = None, filename: str = None) -> list:
    """
    Route to appropriate extractor based on language
    """
    if language is None:
        language = detect_language(code, filename)
    
    if language == 'python':
        return extract_identifiers_python(code)
    elif language == 'javascript':
        return extract_identifiers_javascript(code)
    else:
        # Fallback to Python for unknown languages
        return extract_identifiers_python(code)


# ── MAPPING & MASKING (language-agnostic) ────────────

def build_mapping(identifiers: list, skip_classes=False, skip_functions=False, 
                   skip_parameters=False, skip_variables=False) -> dict:
    mapping = {}
    class_count = 1
    func_count = 1
    param_count = 1
    var_count = 1

    for id_type, name in identifiers:
        if id_type == 'class' and not skip_classes:
            mapping[name] = f'Class{class_count}'
            class_count += 1
        elif id_type == 'function' and not skip_functions:
            mapping[name] = f'method{func_count}'
            func_count += 1
        elif id_type == 'parameter' and not skip_parameters:
            mapping[name] = f'param{param_count}'
            param_count += 1
        elif id_type == 'variable' and not skip_variables:
            mapping[name] = f'var{var_count}'
            var_count += 1

    return mapping


def mask_code(code: str, mapping: dict) -> str:
    masked = code
    for real, masked_name in sorted(mapping.items(),
                                     key=lambda x: len(x[0]),
                                     reverse=True):
        masked = re.sub(r'\b' + re.escape(real) + r'\b',
                        masked_name, masked)
    return masked


def unmask_code(masked_response: str, mapping: dict) -> str:
    reverse_mapping = {v: k for k, v in mapping.items()}
    unmasked = masked_response
    for masked_name, real in sorted(reverse_mapping.items(),
                                     key=lambda x: len(x[0]),
                                     reverse=True):
        unmasked = re.sub(r'\b' + re.escape(masked_name) + r'\b',
                          real, unmasked)
    return unmasked


def save_mapping(mapping: dict, filepath: str = 'mapping.json'):
    # Silent save — no print so extension gets clean output
    with open(filepath, 'w') as f:
        json.dump(mapping, f, indent=2)


def load_mapping(filepath: str = 'mapping.json') -> dict:
    with open(filepath, 'r') as f:
        return json.load(f)


# ── CLI ───────────────────────────────────────────────
if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('action', choices=['mask', 'unmask', 'test'])
    arg_parser.add_argument('--code', type=str)
    arg_parser.add_argument('--file', type=str)
    arg_parser.add_argument('--lang', type=str, choices=['python', 'javascript', 'auto'], default='auto',
                           help='Language: python, javascript, or auto-detect')
    arg_parser.add_argument('--mapping', type=str, default='mapping.json')
    arg_parser.add_argument('--response', type=str)
    arg_parser.add_argument('--skip-classes', action='store_true', help='Do not mask class names')
    arg_parser.add_argument('--skip-functions', action='store_true', help='Do not mask function names')
    arg_parser.add_argument('--skip-parameters', action='store_true', help='Do not mask parameters')
    arg_parser.add_argument('--skip-variables', action='store_true', help='Do not mask variables')
    args = arg_parser.parse_args()

    # ── MASK ─────────────────────────────────────────
    if args.action == 'mask':
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                code = f.read()
            filename = args.file
        elif args.code:
            code = args.code
            filename = None
        else:
            sys.stderr.write("Error: provide --code or --file\n")
            sys.exit(1)

        # Detect language
        if args.lang == 'auto':
            language = detect_language(code, filename)
        else:
            language = args.lang

        identifiers = extract_identifiers(code, language, filename)
        mapping = build_mapping(
            identifiers,
            skip_classes=args.skip_classes,
            skip_functions=args.skip_functions,
            skip_parameters=args.skip_parameters,
            skip_variables=args.skip_variables
        )
        masked = mask_code(code, mapping)
        save_mapping(mapping, args.mapping)

        # ONLY this prints — clean output for extension
        print(masked, end='')

    # ── UNMASK ───────────────────────────────────────
    elif args.action == 'unmask':
        if not args.response:
            sys.stderr.write("Error: provide --response\n")
            sys.exit(1)

        mapping = load_mapping(args.mapping)
        unmasked = unmask_code(args.response, mapping)

        # ONLY this prints — clean output for extension
        print(unmasked, end='')

    # ── TEST ─────────────────────────────────────────
    elif args.action == 'test':
        # Test Python code
        python_test = """
class CustomerInvoiceService:
    def calculate_gst(self, invoice_total, gst_rate):
        taxable_amount = invoice_total * gst_rate
        return taxable_amount

    def generate_invoice(self, customer_name, amount):
        invoice_data = {
            'customer': customer_name,
            'total': amount
        }
        return invoice_data
"""
        
        # Test JavaScript code
        js_test = """
class PaymentProcessor {
    async processPayment(customerData, amount) {
        const transaction = await this.createTransaction(amount);
        return transaction;
    }
    
    createTransaction(totalAmount) {
        const transactionId = generateId();
        return { id: transactionId, amount: totalAmount };
    }
}

const calculateDiscount = (price, discountRate) => {
    return price * (1 - discountRate);
};

function validateCard(cardNumber, expiryDate) {
    const isValid = checkLuhn(cardNumber);
    return isValid;
}
"""

        print("\n" + "="*60)
        print("  PYTHON TEST")
        print("="*60)
        identifiers = extract_identifiers(python_test, 'python')
        mapping = build_mapping(identifiers)
        masked = mask_code(python_test, mapping)
        
        for real, masked_name in mapping.items():
            print(f"  {real:40} → {masked_name}")
        print("\nMASKED:")
        print(masked)

        print("\n" + "="*60)
        print("  JAVASCRIPT TEST")
        print("="*60)
        identifiers = extract_identifiers(js_test, 'javascript')
        mapping = build_mapping(identifiers)
        masked = mask_code(js_test, mapping)
        
        for real, masked_name in mapping.items():
            print(f"  {real:40} → {masked_name}")
        print("\nMASKED:")
        print(masked)
