"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const index_js_1 = require("@modelcontextprotocol/sdk/client/index.js");
const stdio_js_1 = require("@modelcontextprotocol/sdk/client/stdio.js");
const readline = __importStar(require("node:readline/promises"));
const node_process_1 = require("node:process");
async function main() {
    // Create transport to communicate with Python MCP server
    const transport = new stdio_js_1.StdioClientTransport({
        command: "python",
        args: ["mcp_server.py"]
    });
    // Create MCP client
    const client = new index_js_1.Client({
        name: "string-reverser-client",
        version: "1.0.0"
    }, {
        capabilities: {
            tools: {}
        }
    });
    // Connect to the server
    await client.connect(transport);
    console.log("Connected to MCP server");
    // Create readline interface
    const rl = readline.createInterface({ input: node_process_1.stdin, output: node_process_1.stdout });
    // Get input from user
    const text = await rl.question('Enter text to reverse: ');
    rl.close();
    // Call the reverse_string tool
    const result = await client.callTool({
        name: "reverse_string",
        arguments: { text }
    });
    // Print the result
    console.log(`Reversed text: ${result.content[0].text}`);
}
main().catch(console.error);
