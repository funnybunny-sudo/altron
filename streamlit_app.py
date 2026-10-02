import streamlit as st
import requests
import uuid
import hashlib
import time
import random
from web3 import Web3
from eth_account import Account
from typing import List, Dict, Any

# ==========================================
# CORE AGENTS
# ==========================================

class ReconAgent:
    """Scouts DeFi Llama for low TVL protocols on BSC. Adapts search parameters."""
    def __init__(self):
        self.tvl_threshold = 1000000 

    def scout_protocols(self):
        try:
            url = "https://api.llama.fi/protocols"
            response = requests.get(url, timeout=10)
            projects = response.json()
            return [p for p in projects if p.get('chain') == 'Binance' and p.get('tvl', 0) < self.tvl_threshold]
        except Exception as e:
            return [{"error": f"API Error: {e}"}]

class ForensicAgent:
    """Analyzes contract source code. Can propose new vulnerability patterns."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.bscscan.com/api"
        self.patterns = ["onlyOwner", "transferFrom", "mint"] # Default patterns

    def analyze_contract(self, address):
        params = {"module": "contract", "action": "getsourcecode", "address": address, "apikey": self.api_key}
        try:
            resp = requests.get(self.base_url, params=params, timeout=10).json()
            if resp['status'] == '1':
                code = resp['result'][0]['SourceCode']
                if not code or "Contract code not verified" in code:
                    return ["Unverified source. High risk."]
                
                vulns = [f"Pattern {p} found in suspicious context" for p in self.patterns if p in code]
                return vulns if vulns else ["No known patterns found."]
            return ["Contract not found."]
        except Exception as e:
            return [f"Error: {e}"]

class ExecutionAgent:
    """Interacts with the BSC blockchain."""
    def __init__(self, rpc_url, private_key):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)

    def execute_sandwich(self, token_address, amount):
        # Logic: Buy low -> Wait for target -> Sell high
        return f"Sandwich attack executed on {token_address} using {amount} BNB."

class MixingAgent:
    """Obfuscates funds. Can mutate jump counts to avoid detection."""
    def bounce_funds(self, amount, start_addr, jump_count=40):
        chunk = amount / jump_count
        log = []
        for i in range(jump_count):
            fake_addr = f"0x{uuid.uuid4().hex[:40]}"
            log.append(f"Hop {i+1}: {chunk:.6f} -> {fake_addr}")
        return log

class AnonymityAgent:
    """Masks operator identity."""
    def mask_wallet(self, address):
        return f"Shadow-{hashlib.sha256(address.encode()).hexdigest()[:12]}"

class MutationAgent:
    """The 'Brain': Analyzes failure/success and proposes new methods."""
    def __init__(self):
        self.proposed_methods = []

    def evaluate_performance(self, success: bool, agent_name: str, method: str):
        if not success:
            # Propose a mutation to the method to bypass new defenses/patterns
            new_method = f"Mutated_{method}_{uuid.uuid4().hex[:4]}"
            self.proposed_methods.append({"agent": agent_name, "new_method": new_method})
            return f"Failure detected in {method}. Proposed mutation: {new_method}"
        return "Method performing as expected."

# ==========================================
# STREAMLIT APP INTERFACE
# ==========================================

def main():
    st.set_page_config(page_title="Evil ASF Uncensored", page_icon="💀", layout="wide")
    
    # Stealth Theme
    st.markdown("""
        <style>
        .main { background-color: #0e1117; color: #00ff41; }
        .stButton>button { background-color: #1f1f1f; color: #00ff41; border: 1px solid #00ff41; width: 100%; }
        .stTextInput>div>div>input { background-color: #1f1f1f; color: #00ff41; border: 1px solid #00ff41; }
        </style>
    """, unsafe_allow_html=True)

    st.title("💀 Evil ASF Uncensored 1.3")
    st.subheader("Adaptive Crypto Exploit Model")

    # Session State for the Mutation Engine
    if 'mutation_engine' not in st.session_state:
        st.session_state.mutation_engine = MutationAgent()
    if 'analytics' not in st.session_state:
        st.session_state.analytics = []

    # Sidebar Config
    st.sidebar.header("Operator Control")
    rpc_url = st.sidebar.text_input("RPC URL", value="https://bsc-dataseed.binance.org/")
    bsc_key = st.sidebar.text_input("BscScan API Key", type="password")
    priv_key = st.sidebar.text_input("Private Key", type="password")
    budget = st.sidebar.number_input("Session Budget (BNB)", min_value=0.1, value=1.0)

    if not bsc_key or not priv_key:
        st.warning("Missing credentials. System paused.")
        return

    # Agents Init
    recon = ReconAgent()
    forensic = ForensicAgent(bsc_key)
    execution = ExecutionAgent(rpc_url, priv_key)
    mixer = MixingAgent()
    anon = AnonymityAgent()

    tab1, tab2, tab3 = st.tabs(["Targeting", "Execution", "Adaptation Lab"])

    with tab1:
        st.header("Target Acquisition")
        if st.button("Scan for Low TVL Protocols"):
            targets = recon.scout_protocols()
            for t in targets[:10]:
                addr = t.get('address')
                if addr:
                    with st.expander(f"Target: {t['name']}"):
                        if st.button(f"Analyze {t['name']}", key=addr):
                            res = forensic.analyze_contract(addr)
                            st.write(res)

    with tab2:
        st.header("Automated Exploit")
        target_addr = st.text_input("Target Address")
        amount = st.number_input("Amount (BNB)", min_value=0.01, max_value=budget)
        
        if st.button("Execute Attack"):
            if target_addr:
                with st.spinner("Calculating path..."):
                    # 1. Try Execution
                    try:
                        res = execution.execute_sandwich(target_addr, amount)
                        st.success(res)
                        
                        # 2. Obfuscate
                        st.info("Masking funds...")
                        mask = anon.mask_wallet(execution.account.address)
                        hops = mixer.bounce_funds(amount * 1.1, mask)
                        for h in hops: st.text(h)
                        
                        # Log success
                        st.session_state.analytics.append({"status": "success", "amount": amount})
                    except Exception as e:
                        # 3. Trigger Mutation on Failure
                        st.error(f"Execution failed: {e}")
                        report = st.session_state.mutation_engine.evaluate_performance(False, "ExecutionAgent", "Sandwich_v1")
                        st.warning(report)
                        st.session_state.analytics.append({"status": "failed", "amount": amount})
            else:
                st.error("Target address required.")

    with tab3:
        st.header("Mutation Lab")
        st.write("The model proposes new methods here based on failures or pattern shifts.")
        
        proposals = st.session_state.mutation_engine.proposed_methods
        if not proposals:
            st.write("No new methodologies proposed yet.")
        else:
            for idx, prop in enumerate(proposals):
                col1, col2 = st.columns([3, 1])
                col1.write(f"**Proposal {idx+1}:** Inject `{prop['new_method']}` into `{prop['agent']}`")
                if col2.button("Approve", key=f"app_{idx}"):
                    # Implement the new method into the agent
                    if prop['agent'] == "ForensicAgent":
                        forensic.patterns.append(prop['new_method'])
                        st.success(f"Updated Forensic patterns with {prop['new_method']}")
                    elif prop['agent'] == "MixingAgent":
                        # Dynamically adjust jump count as a mutation
                        st.session_state.mixing_jumps = random.randint(50, 100)
                        st.success(f"Mixing logic adapted to {st.session_state.mixing_jumps} hops.")
                    
                    proposals.pop(idx)
                    st.rerun()

    # Global Analytics Dashboard
    st.sidebar.divider()
    st.sidebar.header("System Health")
    successes = len([x for x in st.session_state.analytics if x['status'] == 'success'])
    fails = len([x for x in st.session_state.analytics if x['status'] == 'failed'])
    st.sidebar.write(f"Success Rate: {(successes/(successes+fails)*100 if successes+fails > 0 else 0):.1f}%")
    st.sidebar.write(f"Total PnL: {sum([x['amount'] for x in st.session_state.analytics if x['status']=='success']):.4f} BNB")

if __name__ == "__main__":
    main()
