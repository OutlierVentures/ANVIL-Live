import os, requests, time, json
from quart import Quart, render_template, redirect, url_for, session, request, jsonify
from sovrin.utilities import generate_base58
from sovrin.setup import setup_pool, set_self_up
from sovrin.onboarding import demo_onboard
from sovrin.schema import create_schema, create_credential_definition
from sovrin.credentials import offer_credential, receive_credential_offer, request_credential, create_and_send_credential, store_credential
app = Quart(__name__)

debug = False # Do not enable in production
host = '0.0.0.0'
port = 5004

@app.before_first_request
async def initialize():
    global pool_name, pool_handle, issuer, prover, verifier
    # Pool setup and onboarding.
    # In many cases this would most likely be done prior to any transactions.
    pool_name, pool_handle = await setup_pool('local')
    steward = await set_self_up('steward', generate_base58(64), generate_base58(64), pool_handle,
                                seed = '000000000000000000000000Steward1')
    issuer = await set_self_up('issuer', generate_base58(64), generate_base58(64), pool_handle)
    prover = await set_self_up('prover', generate_base58(64), generate_base58(64), pool_handle)
    verifier = await set_self_up('verifier', generate_base58(64), generate_base58(64), pool_handle)
    steward, issuer = await demo_onboard(steward, issuer)
    steward, verifier = await demo_onboard(steward, verifier)
    issuer, prover = await demo_onboard(issuer, prover)
    verifier, prover = await demo_onboard(verifier, prover)
    # Create schema and corresponding definition.
    # In many cases this would most likely be done prior to any transactions.
    schema = {
        "name": "Charging Station Certification",
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
    global issuer, prover
    # For inter-actor interaction check oput the ANVIL Apps
    issuer, prover['authcrypted_cred_offer'] = await offer_credential(issuer, 'charging_station_certification')  
    prover = await receive_credential_offer(prover)
    request = json.dumps({
        "output": {"raw": "22kW", "encoded": "22"},
        "grounded": {"raw": "yes", "encoded": "1"},
        "license": {"raw": "Grounded Station", "encoded": "145"},
        "firmware": {"raw": "4.5", "encoded": "45"},
        "year": {"raw": "2019", "encoded": "2019"},
        "id": {"raw": "did:ov:37h3r", "encoded": "3708318"}
    })
    prover, issuer['authcrypted_cred_request'] = await request_credential(prover, request)
    issuer, prover['authcrypted_cred'] = await create_and_send_credential(issuer)
    prover = await store_credential(prover)
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
    
