from flask import Flask, render_template, request, jsonify
import math
import random

app = Flask(__name__)

def get_aridaq_potential(r, debye, salt):
    # Core Formula: f * e^(-kr) / (r + screening)
    k = 1 / (debye * math.sqrt(salt + 0.00001))
    return (3.17e9 * math.exp(-k * r)) / (r + 0.026)

@app.route('/simulate_bio', methods=['POST'])
def simulate_bio():
    data = request.json
    seq = data.get('sequence', 'MKTIIALSYIFCLVFA')
    ph = float(data.get('ph', 7.4))
    salt = float(data.get('salt', 0.15))
    
    debye = 5000 + ((7.4 - ph) * 200)
    nodes = []
    last_pos = [0, 0, 0]
    
    for i, char in enumerate(seq):
        # Using a helical growth pattern for "Real" folding appearance
        angle = i * 0.5
        radius = 2.0 + random.uniform(-0.5, 0.5)
        
        new_x = last_pos[0] + radius * math.cos(angle)
        new_y = last_pos[1] + 1.5 # Consistent rise per residue
        new_z = last_pos[2] + radius * math.sin(angle)
        
        r = math.sqrt(new_x**2 + new_y**2 + new_z**2)
        pot = get_aridaq_potential(r, debye, salt)
        
        # Determine "Color Type" based on potential
        color_type = "helix" if pot > 1e10 else "loop"
        
        nodes.append({
            "id": i, "type": char, "struct": color_type,
            "x": new_x, "y": new_y, "z": new_z,
            "u": f"{pot:.2e}"
        })
        last_pos = [new_x, new_y, new_z]

    return jsonify({"nodes": nodes, "metrics": {"debye": debye, "salt": salt}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
if __name__ == "__main__":
    # 0.0.0.0 is the magic number that lets the Replit preview see your app
    app.run(host="0.0.0.0", port=5000, debug=True)


    
        
    
    