import os, requests, time, json
from quart import Quart, render_template, redirect, url_for, session, request, jsonify
from sovrin.utilities import generate_base58
from sovrin.setup import setup_pool, set_self_up
from sovrin.onboarding import demo_onboard
from sovrin.schema import create_schema, create_credential_definition
from common import common_setup, common_connection_request, common_establish_channel, common_verinym_request, common_reset
app = Quart(__name__)

debug = False # Do not enable in production
host = '0.0.0.0'
port = 5004

@app.before_first_request
async def initialize():
    global pool_name, pool_handle, issuer, prover, verifier
    # Pool setup and onboarding. For simplicity Steward is also issuer.
    # In many cases this would most likely be done prior to any transactions.
    pool_name, pool_handle = await setup_pool('local')
    issuer = await set_self_up('issuer', generate_base58(64), generate_base58(64), pool_handle,
                            seed = '000000000000000000000000Steward1')
    prover = await set_self_up('prover', generate_base58(64), generate_base58(64), pool_handle)
    verifier = await set_self_up('verifier', generate_base58(64), generate_base58(64), pool_handle)
    issuer, prover = await demo_onboard(issuer, prover)
    issuer, verifier = await demo_onboard(issuer, verifier)
    # Create schema and corresponding definition.
    # In many cases this would most likely be done prior to any transactions.
    schema = {
        "name": "Charging Pole Certification",
        "version": "1.0",
        "attributes": ["output", "grounded", "license", "firmware", "year", "id"]
    }
    unique_schema_name, schema_id, issuer = await create_schema(schema, issuer)
    issuer = await create_credential_definition(issuer, schema_id, unique_schema_name, revocable = False)
    # Open channel between transacting actors
    verifier, prover = await demo_onboard(verifier, prover)


@app.route('/')
def index():
    global pool_name, pool_handle, issuer, prover, verifier
    setup = True if issuer and prover and verifier else False
    return render_template('demo.html', setup = setup)


@app.route('/issue', methods = ['GET', 'POST'])
async def issue():
    return redirect(url_for('index'))


@app.route('/preq', methods = ['GET', 'POST'])
async def preq():
    return redirect(url_for('index'))


@app.route('/purchase', methods = ['GET', 'POST'])
async def establish_channel():
    # Reset
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = os.getenv('ANVIL_KEY', 'MUST_BE_STATIC')
    app.run(host, port, debug)
    
