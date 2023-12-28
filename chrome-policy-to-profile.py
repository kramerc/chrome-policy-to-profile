#!/usr/bin/env python3
import argparse
import json
import plistlib
import uuid

PROFILE_TYPE = 'com.kramerc.ChromePolicyToProfile'
PAYLOAD_CONTENT_TYPES = {
    'Google Chrome': 'com.google.Chrome',
    'Microsoft Edge': 'com.microsoft.Edge',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Input JSON file (e.g., policies.json)')
    parser.add_argument('output', help='Output mobileconfig file (e.g., policies.mobileconfig)')
    args = parser.parse_args()

    with open(args.input, 'rb') as f:
        mobileconfig = {
            'PayloadContent': [{}]
        }

        # Read JSON
        json_data = json.load(f)
        json_policies = json_data['policyValues']['chrome']['policies']
        for policy in json_policies:
            mobileconfig['PayloadContent'][0][policy] = json_policies[policy]['value']

        # Determine PayloadContent's PayloadType
        content_type = ''
        if json_data['chromeMetadata']['application'] in PAYLOAD_CONTENT_TYPES:
            content_type = PAYLOAD_CONTENT_TYPES[json_data['chromeMetadata']['application']]
        else:
            raise Exception('Unknown application: ' + json_data['chromeMetadata']['application'])

        # Generate UUIDs and build identifiers
        mobileconfig_uuid = str(uuid.uuid4()).upper()
        content_uuid = str(uuid.uuid4()).upper()
        mobileconfig_identifier = PROFILE_TYPE + '.' + mobileconfig_uuid
        content_identifier = mobileconfig_identifier + '.' + content_type + '.' + content_uuid

        # Build PayloadContent
        mobileconfig['PayloadContent'][0]['PayloadDisplayName'] = json_data['chromeMetadata']['application']
        mobileconfig['PayloadContent'][0]['PayloadIdentifier'] = content_identifier
        mobileconfig['PayloadContent'][0]['PayloadOrganization'] = ''
        mobileconfig['PayloadContent'][0]['PayloadType'] = content_type
        mobileconfig['PayloadContent'][0]['PayloadUUID'] = content_uuid
        mobileconfig['PayloadContent'][0]['PayloadVersion'] = 1

        # Build top level properties
        mobileconfig['PayloadDisplayName'] = json_data['policyValues']['chrome']['name']
        mobileconfig['PayloadIdentifier'] = PROFILE_TYPE + '.' + mobileconfig_uuid
        mobileconfig['PayloadOrganization'] = 'ChromePolicyToProfile'
        mobileconfig['PayloadScope'] = 'User'
        mobileconfig['PayloadType'] = 'Configuration'
        mobileconfig['PayloadUUID'] = mobileconfig_uuid
        mobileconfig['PayloadVersion'] = 1

        # Write plist
        plist_data = plistlib.dumps(mobileconfig)
        with open(args.output, 'wb') as g:
            g.write(plist_data)


if __name__ == '__main__':
    main()
