const { spawn } = require("child_process");

const pythonBot = spawn("python", ["bot.py"]);
const nodeBot = spawn("node", ["index.js"]);

pythonBot.stdout.on("data", (data) => {
  console.log(`[Python Bot]: ${data}`);
});

pythonBot.stderr.on("data", (data) => {
  console.error(`[Python Bot Error]: ${data}`);
});

nodeBot.stdout.on("data", (data) => {
  console.log(`[Node Bot]: ${data}`);
});

nodeBot.stderr.on("data", (data) => {
  console.error(`[Node Bot Error]: ${data}`);
});

pythonBot.on("close", (code) => {
  console.log(`[Python Bot] Process exited with code ${code}`);
});

nodeBot.on("close", (code) => {
  console.log(`[Node Bot] Process exited with code ${code}`);
});
