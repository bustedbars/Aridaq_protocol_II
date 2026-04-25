from flask import Flask, render_template, request, jsonify
import math
import random

app = Flask(__name__)

# --- THE ARIDAQ CORE LOGIC ---
SCALING_FACTOR = 3.17 * 10**9  
DEBYE_LENGTH = 5000             
SCREENING_CONST = 0.026      

# --- BIOLOGY CONSTANTS (Simplified) ---
AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY" # Standard 20 amino acids

def calculate_yukawa_potential(r, debye=DEBYE_LENGTH):
    if r <= 0: r = 1e-9 # Avoid division by zero
    # f * e^(-kr) / r
    u = (SCALING_FACTOR * math.exp(-r/debye)) / (r + SCREENING_CONST)
    return u

def mutate_sequence(sequence):
    """Randomly swaps one amino acid in the sequence."""
    if not sequence: return sequence
    seq_list = list(sequence)
    index_to_mutate = random.randint(0, len(seq_list) - 1)
    
    current_aa = seq_list[index_to_mutate]
    available_mutations = [aa for aa in AMINO_ACIDS if aa != current_aa]
    new_aa = random.choice(available_mutations)
    
    seq_list[index_to_mutate] = new_aa
    mutated_seq = "".join(seq_list)
    
    return mutated_seq, index_to_mutate, current_aa, new_aa

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate_bio', methods=['POST'])
def simulate_bio():
    data = request.json
    sequence = data.get('sequence', 'MKTIIALSYIFCLVFA')
    temperature = int(data.get('temp', 310))
    is_mutation = data.get('mutation_mode', False)
    
    # We always simulate the normal one first, then potentially the mutated one
    original_sequence = data.get('original_sequence', sequence)
    active_sequence = sequence
    
    if is_mutation:
        active_sequence, mutated_index, old_aa, new_aa = mutate_sequence(sequence)
        
    # Standard seed for normal, different seed for mutation
    random.seed(42 if not is_mutation else 101) 
    
    nodes = []
    total_u = 0
    
    # We simulate a slightly more structured "movie" based on the sequence
    # For a mutation, we introduce instability or a "collision"
    for i in range(len(active_sequence)):
        # Introduce temperature effects (simulated volatility)
        temp_volatility = (temperature - 310) / 100 
        
        # Base Aridaq placement logic
        base_x = random.uniform(-10, 10)
        base_y = random.uniform(-10, 10)
        base_z = random.uniform(-10, 10)
        
        # For mutation, add instability at the mutated index
        if is_mutation and i == mutated_index:
            base_x += random.uniform(-5, 5) * (1 + temp_volatility)
            base_z += random.uniform(-5, 5) * (1 + temp_volatility)

        nodes.append({
            "id": i,
            "x": base_x,
            "y": base_y,
            "z": base_z,
            "potential": 0 # We will calc this next
        })
        
    # --- The "Movie" and Bond Angles ---
    # We use Aridaq scaling to determine relative "forces"
    for i in range(len(nodes)):
        r = math.sqrt(nodes[i]['x']**2 + nodes[i]['y']**2 + nodes[i]['z']**2)
        nodes[i]['potential'] = calculate_yukawa_potential(r)
        total_u += nodes[i]['potential']
        
    response_data = {
        "nodes": nodes,
        "total_potential": f"{total_u:.4e}",
        "active_sequence": active_sequence,
        "status": "FOLDING_COMPLETE"
        
    }
    
    if is_mutation:
        response_data['mutation_details'] = f"{old_aa}{mutated_index+1}{new_aa}"
        response_data['original_sequence'] = original_sequence

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

