# QuestMind

A WebAssembly project built with Rust that demonstrates basic WASM functionality.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Rust](https://rustup.rs/) (latest stable version)
- [wasm-pack](https://rustwasm.github.io/wasm-pack/installer/)

### Installing Prerequisites

1. Install Rust:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

2. Install wasm-pack:
```bash
curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh
```

## Building the Project

To build the WebAssembly module:

```bash
wasm-pack build --target web
```

This will generate the WASM module and JavaScript bindings in the `pkg/` directory.

## Running the Demo

1. Build the project:
```bash
npm run build
```

2. Start a local server:
```bash
npm run serve
```

3. Open your browser and navigate to `http://localhost:8000`

## Project Structure

- `src/lib.rs` - Main Rust source code with WASM exports
- `src/main.rs` - Not used (library crate)
- `Cargo.toml` - Rust project configuration
- `index.html` - Demo HTML page
- `package.json` - npm scripts for building and serving
- `pkg/` - Generated WASM module and JS bindings (after build)

## Functions Exported to JavaScript

- `greet(name: string)` - Logs a greeting message to console
- `add(a: number, b: number): number` - Adds two numbers
- `process_text(text: string): string` - Processes and transforms text

## Development

For development with auto-rebuild:
```bash
npm run dev
```

## License

MIT

# questmind