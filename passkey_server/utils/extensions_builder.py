import json

with open("config/extensions_config.json") as f:
    EXTENSION_POLICIES = json.load(f)

def get_webauthn_extensions_for_org(org_id: str) -> dict:
    config = EXTENSION_POLICIES.get(org_id, {})
    print(config,'config')
    extensions = {}
    if config.get("credProps"):
        extensions["credProps"] = True

    if isinstance(config.get("credProtect"), dict):
        extensions["credProtect"] = {
            "credentialProtectionPolicy": config["credProtect"]["level"],
            "enforceCredentialProtectionPolicy": config["credProtect"].get("enforce", False)
        }

    if config.get("largeBlob"):
        extensions["largeBlob"] = { "support": "preferred" }

    if isinstance(config.get("payment"), dict):
        extensions["payment"] = config["payment"]

    if isinstance(config.get("txAuthSimple"), str):
        extensions["txAuthSimple"] = config["txAuthSimple"]

    if isinstance(config.get('discoverable'), bool):
        extensions['discoverable'] = config['discoverable']

    if isinstance(config.get('authenticator_attachment'), str):
        extensions['authenticator_attachment'] = config['authenticator_attachment']
        
    if isinstance(config.get('custom_metadata'), dict):
        extensions['custom_metadata'] = config['custom_metadata']

    print(extensions, 'extensions')
    return extensions
