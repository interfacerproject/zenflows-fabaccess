import type { NextApiRequest, NextApiResponse } from "next";
import { zencode_exec } from "zenroom";
import fabaccessCmd from "../../crypto/src/sign_fabaccess_cmd";

type Data = {
  result: string;
  query: string;
};

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<Data>
) {
  const input = {
    command: "ON",
    service: "urn:fabaccess:resource:Another",
    timestamp: new Date().getTime().toString().slice(0, -3),
    token: "bm90LWltcGxlbWVudGVk",
    keyring: {
      eddsa: "Cwj9CcqHNoBnXBo8iDfnhFkQeDun4Y4LStd2m3TEAYAg",
    },
  };
  const contract = fabaccessCmd();
  const pk = zencode_exec(contract, { keys: JSON.stringify(input) }).then(
    async (r) => {
      console.log("SENDIND TO FABACCESS", r.result);
      const resp = await fetch(
        "https://fabaccess.interfacer.dyne.org/command",
        {
          method: "post",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },

          //make sure to serialize your JSON body
          body: r.result,
        }
      );
      const result = await resp.json();
      res.status(200).json({ result: result, query: JSON.parse(r.result) });
    }
  );
}
