# Ollama Optimization for AI-Socratic-Clarifier

This document describes the optimization settings for Ollama used in AI-Socratic-Clarifier to improve performance.

## Optimization Settings

The following optimizations have been applied:

1. **Context Window Size**: Increased from 2048 to 8192 tokens
   - Allows for longer conversations and more document context
   - Modified in `config.json` under `integrations.ollama.context_length`

2. **Flash Attention**: Enabled
   - Significantly reduces memory usage as context size grows
   - Set via environment variable `OLLAMA_FLASH_ATTENTION=1`

3. **KV Cache Quantization**: Set to q8_0 (8-bit)
   - Uses approximately 1/2 the memory of f16 with minimal quality loss
   - Set via environment variable `OLLAMA_KV_CACHE_TYPE=q8_0`

## Using Optimized Settings

### Option 1: Use the Provided Script

Run the application with optimized settings using:

```bash
./start_with_optimized_ollama.sh
```

This script sets the necessary environment variables and starts the application.

### Option 2: Manual Configuration

1. Set environment variables before starting Ollama:

```bash
export OLLAMA_CONTEXT_LENGTH=8192
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KV_CACHE_TYPE=q8_0
ollama serve
```

2. Ensure the `config.json` file has the matching context length:

```json
"ollama": {
    ...
    "context_length": 8192,
    ...
}
```

## Advanced Configurations

For even more optimization, consider:

1. **Parallel Requests**: Control with `OLLAMA_NUM_PARALLEL` (default is auto-select 4 or 1 based on available memory)

2. **Maximum Queue**: Set with `OLLAMA_MAX_QUEUE` (default is 512)

3. **More Aggressive Quantization**: For very large contexts, you can use `q4_0` which uses approximately 1/4 the memory of f16 but with more noticeable quality loss:

```bash
export OLLAMA_KV_CACHE_TYPE=q4_0
```

## Troubleshooting

If you encounter "out of memory" errors:

1. Try lowering the context length to 4096 in both the environment variable and config.json
2. Use more aggressive quantization with `q4_0`
3. Reduce the `OLLAMA_NUM_PARALLEL` to 1

## Effects on Performance

| Setting | Memory Usage | Quality Impact |
|---------|--------------|----------------|
| Default (f16) | Baseline | None |
| q8_0 | ~50% reduction | Very minor |
| q4_0 | ~75% reduction | Noticeable |

These optimizations are especially important when using models with larger contexts or when processing multiple documents.
