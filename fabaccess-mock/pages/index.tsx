import Head from "next/head";
import { Inter } from "@next/font/google";
import styles from "@/styles/Home.module.css";
import { useState } from "react";

const inter = Inter({ subsets: ["latin"] });
type TS = {
  timestamp: string;
  state: string;
  result: string;
};
export default function Home() {
  const [message, setMessage] = useState("");
  const [on, setOn] = useState(false);
  const [logs, setLogs] = useState<TS[]>([]);

  return (
    <>
      <Head>
        <title>Fabaccess Demo</title>
        <meta name="description" content="Dyne.org::Loves fabaccess" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className={styles.main}>
        <button
          className={styles.button}
          onClick={async () => {
            const res = await fetch(`/api/${on ? "off" : "on"}`);
            const data = await res.json();
            setMessage(JSON.stringify(data, null, 2));
            setLogs([
              {
                timestamp: data.query.timestamp,
                state: data.query.command,
                result: JSON.stringify(data.result),
              },
              ...logs,
            ]);
            setOn(!on);
          }}
        >
          {on ? "OFF" : "ON"}
        </button>
        <pre style={{ overflow: "auto" }}>{message}</pre>
        <div
          style={{
            border: "2px solid green",
            padding: "20px",
            maxHeight: "400px",
            width: "60%",
            overflow: "scroll",
          }}
        >
          <h3>LOG</h3>
          <ul>
            {logs.map((l) => {
              return (
                <li style={{ paddingTop: "10px" }}>
                  {l.state} @{l.timestamp} <br /> RESULT: {l.result} <br />
                </li>
              );
            })}
          </ul>
        </div>
      </main>
    </>
  );
}
