import streamlit as st
import math

# Constants
PIPE_TYPES = {
    "steel": 0.00015,
    "cast iron": 0.00026,
    "concrete": 0.003,
    "PVC": 0.0000015,
    "copper tubing": 0.0000015
}
rho = 1000
mu = 1e-3
g = 9.81

def colebrook_white(Re, epsilon, D):
    if Re < 2000:
        return 64 / Re
    f = 0.02
    for _ in range(50):
        f_old = f
        f = 1 / (-2 * math.log10((epsilon / (3.7 * D)) + (2.51 / (Re * math.sqrt(f))))) ** 2
        if abs(f - f_old) < 1e-6:
            break
    return f

def solve_velocity_from_head_loss(L, D, h_f, epsilon):
    f = 0.02
    for _ in range(100):
        V = math.sqrt((2 * g * h_f * D) / (f * L))
        Re = (rho * V * D) / mu
        f_new = colebrook_white(Re, epsilon, D)
        if abs(f_new - f) < 1e-6:
            break
        f = f_new
    return V, f, Re

# Streamlit UI
st.title("Pipe Major Loss Calculator")

pipe_type = st.selectbox("Select Pipe Type", list(PIPE_TYPES.keys()))
epsilon = PIPE_TYPES[pipe_type]

st.subheader("Enter Known Values (leave unknowns blank):")
L = st.number_input("Pipe Length (m)", min_value=0.0, format="%.2f")
D = st.number_input("Pipe Diameter (m)", min_value=0.0, format="%.3f")
Q = st.text_input("Flow Rate (m³/s)")
V = st.text_input("Velocity (m/s)")
h_f = st.text_input("Major Head Loss (m)")

# Convert input strings to float where possible
Q = float(Q) if Q else None
V = float(V) if V else None
h_f = float(h_f) if h_f else None

if st.button("Calculate"):
    try:
        A = math.pi * D**2 / 4 if D else None

        if V is None and h_f and L and D:
            V, f, Re = solve_velocity_from_head_loss(L, D, h_f, epsilon)
        else:
            if V is None and Q and A:
                V = Q / A
            if Q is None and V and A:
                Q = V * A
            if V and D:
                Re = (rho * V * D) / mu
                f = colebrook_white(Re, epsilon, D)
            if h_f is None and V and L and D:
                h_f = f * (L / D) * V**2 / (2 * g)

        st.success("Calculation Complete")
        st.write(f"**Velocity (m/s):** {V:.4f}" if V else "")
        st.write(f"**Flow Rate (m³/s):** {Q:.6f}" if Q else "")
        st.write(f"**Head Loss (m):** {h_f:.4f}" if h_f else "")
        st.write(f"**Reynolds Number:** {Re:.2f}" if V else "")
        st.write(f"**Friction Factor:** {f:.5f}" if V else "")

    except Exception as e:
        st.error(f"Error: {e}")
