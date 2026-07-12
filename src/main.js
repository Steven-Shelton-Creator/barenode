import { EOL } from "node:os";

const greet = (name = "world") => `Hello, ${name}!`;

console.log(greet("barenode"));
console.log(`Running on Node.js ${process.version}${EOL}`);