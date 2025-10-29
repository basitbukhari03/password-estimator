from flask import Flask, request, jsonify
import string
import math
import sys
import os

app = Flask(__name__)

@app.route('/estimate', methods=['POST'])
def estimate():
    data = request.get_json() or {}
    password = data.get('password', '')

    # Original logic: charset checks
    S = 0
    checklower = any(c.islower() for c in password)
    checkupper = any(c.isupper() for c in password)
    checkdigit = any(c.isdigit() for c in password)
    checkspecial = any(c in string.punctuation for c in password)

    if checklower:
        S += 26
    if checkupper:
        S += 26
    if checkdigit:
        S += 10
    if checkspecial:
        S += 33

    L = len(password)
    R = 10**9

    # Compute time = S**L / R. Protect against overflow for large L by using logs.
    result = {
        'charset_size': S,
        'length': L
    }

    try:
        if S == 0:
            result['error'] = 'No recognized character classes (S=0).'
            return jsonify(result), 400
        # attempt direct computation if small
        if L * math.log(S) < 700:  # safe threshold for exp
            total = S**L
            time_seconds = total / R
            result['time_seconds'] = time_seconds
        else:
            # represent time using scientific notation via logs to avoid overflow
            # log10(time_seconds) = (L*log10(S)) - log10(R)
            log10_time = L * math.log10(S) - math.log10(R)
            exponent = math.floor(log10_time)
            mantissa = 10**(log10_time - exponent)
            result['time_seconds_scientific'] = f"{mantissa:.3f}e{exponent}"

        # human friendly conversion if possible
        if 'time_seconds' in result:
            t = result['time_seconds']
            if t > 86400 and t < 2592000:
                result['time_days'] = t / 86400
            elif t >= 2592000:
                result['time_months'] = t / 2592000

    except OverflowError:
        # fallback in the rare case of overflow
        log10_time = L * math.log10(max(S,1)) - math.log10(R if R>0 else 1)
        exponent = math.floor(log10_time)
        mantissa = 10**(log10_time - exponent)
        result['time_seconds_scientific'] = f"{mantissa:.3f}e{exponent}"

    return jsonify(result)

if __name__ == '__main__':
    # bind to port from environment for hosting platforms
    port = int(os.environ.get('PORT', 5000)) if 'os' in globals() else 5000
    app.run(host='0.0.0.0', port=port)
