#!/bin/sh

source "../zenflows-crypto/test/utils.sh"

sk="Cwj9CcqHNoBnXBo8iDfnhFkQeDun4Y4LStd2m3TEAYAg"

cmd="$1"

if [[ "$cmd" != "ON" && "$cmd" != "OFF" ]]; then
  echo "Unknown command $cmd (known commands are ON and OFF)"
  exit 1
fi

echo "SIGNING COMMAND"

cat <<EOF >not_signed.json
{
  "command": "$cmd",
  "service": "urn:fabaccess:resource:Another",
  "timestamp": "`date +%s`",
  "token": "bm90LWltcGxlbWVudGVk",
  "keyring": {
    "eddsa": "$sk"
  }
}
EOF

ts_source='../zenflows-crypto/src/sign_fabaccess_cmd'
echo "$ts_source"
zen_source=`getscript $ts_source`

echo "$zen_source"
zenroom -a not_signed.json -z "$zen_source" >signed.json

cat signed.json

echo "SEND COMMAND"

curl -X POST -H 'Content-Type:application/json' -d "@signed.json" "http://localhost:8000/command"
echo
