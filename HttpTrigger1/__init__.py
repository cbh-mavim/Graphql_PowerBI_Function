import logging
import azure.functions as func
import requests
import os
import json  # Required for proper JSON formatting

def get_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": os.environ["CLIENT_ID"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "scope": os.environ["SCOPE"]
    }
    tenant_id = os.environ["TENANT_ID"]
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    resp = requests.post(token_url, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("GraphQL proxy called.")

    try:
        token = get_token()

        query = {
            "query": """
            query {
                customerAddonsDetails {
                    customerId
                    isAddon
                }
            }
            """
        }

        graphql_url = os.environ["GRAPHQL_URL"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        gql_response = requests.post(graphql_url, json=query, headers=headers)
        gql_response.raise_for_status()

        # Proper JSON serialization
        return func.HttpResponse(
            body=json.dumps(gql_response.json()),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error in Azure Function: {str(e)}")
        return func.HttpResponse(str(e), status_code=500)
