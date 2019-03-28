import os, requests, time, json
from quart import Quart, render_template, redirect, url_for, session, request, jsonify
from sovrin.utilities import generate_base58
from sovrin.setup import setup_pool, set_self_up
from sovrin.onboarding import demo_onboard
from sovrin.schema import create_schema, create_credential_definition
from sovrin.credentials import offer_credential, receive_credential_offer, request_credential, create_and_send_credential, store_credential
from sovrin.proofs import request_proof_of_credential, create_proof_of_credential, verify_proof
from fetch.agents import offer_service, purchase_service
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
    # For inter-machine interaction check out the ANVIL Apps
    global issuer, prover
    issuer, prover['authcrypted_cred_offer'] = await offer_credential(issuer, 'charging_station_certification')  
    prover = await receive_credential_offer(prover)
    cred_request = json.dumps({
        "output": {"raw": "22kW", "encoded": "22"},
        "grounded": {"raw": "yes", "encoded": "1"},
        "license": {"raw": "Grounded Station", "encoded": "145"},
        "firmware": {"raw": "4.5", "encoded": "45"},
        "year": {"raw": "2019", "encoded": "2019"},
        "id": {"raw": "did:ov:37h3r", "encoded": "3708318"}
    })
    prover, issuer['authcrypted_cred_request'] = await request_credential(prover, cred_request)
    issuer, prover['authcrypted_cred'] = await create_and_send_credential(issuer)
    prover = await store_credential(prover)
    offer_service(100, '../../charging_service')
    return redirect(url_for('index'))


@app.route('/verify', methods = ['GET', 'POST'])
async def verify():
    # For inter-machine interaction check out the ANVIL Apps
    global verifier, prover
    form = await request.form
    adjusted_output = form['output'][:-2] + 'kW'
    proof_request = json.dumps({
        "nonce": "0123456789012345678901234",
        "name": "Grounded Station proof",
        "version": "0.1",
        "requested_attributes": {
            "attr1_referent": {
                "name": "output"
            },
            "attr2_referent": {
                "name": "grounded"
            },
            "attr3_referent": {
                "name": "license"
            },
            "attr4_referent": {
                "name": "firmware"
            },
            "attr5_referent": {
                "name": "id"
            }
        },
        "requested_predicates": {
            "predicate1_referent": {
                "name": "year",
                "p_type": ">=",
                "p_value": 2019
            }
        }
    })
    verifier, prover['authcrypted_proof_request'] = await request_proof_of_credential(verifier, proof_request)
    self_attested_attributes = {
        "attr1_referent": "22kW",
        "attr5_referent": "did:ov:37h3r"
    }
    prover, verifier['authcrypted_proof'] = await create_proof_of_credential(prover, self_attested_attributes, [2,3,4], [1], [])
    assertions_to_make = {
        "revealed": {
            "attr2_referent": form['grounded'],
            "attr3_referent": "Grounded Station",
            "attr4_referent": form['firmware']
        },
        "self_attested": {
            "attr1_referent": adjusted_output,
            "attr5_referent": "did:ov:37h3r"
        }
    }
    verifier = await verify_proof(verifier, assertions_to_make)
    # await teardown(pool_name, pool_handle, [steward, issuer, prover, verifier])
    '''
    TODO: redirect to demo_verified or demo_failed
    '''
    return redirect(url_for('index'))


@app.route('/purchase', methods = ['GET', 'POST'])
async def purchase():
    purchase_service(101, 'license_output')
    # Reset
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.secret_key = os.getenv('ANVIL_KEY', 'MUST_BE_STATIC')
    app.run(host, port, debug)
    
