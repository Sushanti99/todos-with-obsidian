import Foundation

/// Writes the default brain.config.yaml into a vault so the Python server can start.
enum BrainConfigWriter {
    static func writeDefaultConfig(vaultPath: String, anthropicKey: String) {
        let vault = URL(fileURLWithPath: vaultPath)
        let systemDir = vault.appendingPathComponent("system")
        let configFile = systemDir.appendingPathComponent("brain.config.yaml")

        try? FileManager.default.createDirectory(at: systemDir, withIntermediateDirectories: true)

        // Always overwrite — ensures vault path and settings stay in sync with what the app knows
        writeEnvFile(anthropicKey: anthropicKey)

        let yaml = """
agent: claude-code
server:
  host: 127.0.0.1
  port: 3000
  auto_open_browser: false
vault:
  path: \(vaultPath)
  daily_folder: daily
  core_folder: core
  references_folder: references
  thoughts_folder: thoughts
  system_folder: system
session:
  single_session: true
  history_turn_limit: 10
  summarize_on_end: true
  auto_save_summary: true
  inactivity_timeout_seconds: 120
agents:
  claude-code:
    command: claude
    args: ["-p", "--output-format", "stream-json", "--verbose"]
    allowed_tools: [Read, Edit, Bash, Glob, Grep]
  codex:
    command: codex
    args: ["exec", "--json", "--sandbox", "workspace-write"]
integrations:
  enable_daily_context: true
  include_in_prompt: false
"""
        try? yaml.write(to: configFile, atomically: true, encoding: .utf8)
    }

    private static func writeEnvFile(anthropicKey: String) {
        let appSupport = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Application Support/BrainSquared")
        try? FileManager.default.createDirectory(at: appSupport, withIntermediateDirectories: true)
        let envFile = appSupport.appendingPathComponent(".env")
        let content = "ANTHROPIC_API_KEY=\(anthropicKey)\n"
        try? content.write(to: envFile, atomically: true, encoding: .utf8)
    }
}
