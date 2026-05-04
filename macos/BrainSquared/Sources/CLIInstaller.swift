import Foundation

enum CLIInstallerError: LocalizedError {
    case nodeNotFound
    case npmFailed(String)

    var errorDescription: String? {
        switch self {
        case .nodeNotFound:
            return "Node.js was not found. Install it from nodejs.org then reopen brain²."
        case .npmFailed(let pkg):
            return "npm install failed for \(pkg)."
        }
    }
}

class CLIInstaller {
    static func installAll(
        anthropicKey: String,
        openaiKey: String?,
        progress: @escaping (String) -> Void,
        completion: @escaping (Error?) -> Void
    ) {
        DispatchQueue.global(qos: .userInitiated).async {
            guard let npm = findNPM() else {
                completion(CLIInstallerError.nodeNotFound)
                return
            }

            var env = ProcessInfo.processInfo.environment
            env["ANTHROPIC_API_KEY"] = anthropicKey
            if let key = openaiKey { env["OPENAI_API_KEY"] = key }
            // Inherit PATH so npm can find itself
            let extraPaths = "/opt/homebrew/bin:/usr/local/bin"
            env["PATH"] = "\(extraPaths):\(env["PATH"] ?? "/usr/bin")"

            progress("Installing @anthropic-ai/claude-code…")
            if run(npm, args: ["install", "-g", "@anthropic-ai/claude-code"], env: env) != nil {
                completion(CLIInstallerError.npmFailed("@anthropic-ai/claude-code"))
                return
            }

            progress("Installing @openai/codex…")
            // Non-fatal — user may not have OpenAI key
            _ = run(npm, args: ["install", "-g", "@openai/codex"], env: env)

            progress("Done!")
            completion(nil)
        }
    }

    // MARK: Helpers

    static func findNPM() -> String? {
        let candidates = [
            "/opt/homebrew/bin/npm",
            "/usr/local/bin/npm",
            "/usr/bin/npm",
        ]
        // Check nvm installations
        let home = FileManager.default.homeDirectoryForCurrentUser.path
        let nvmBase = "\(home)/.nvm/versions/node"
        if let versions = try? FileManager.default.contentsOfDirectory(atPath: nvmBase),
           let latest = versions.filter({ !$0.hasPrefix(".") }).sorted().last {
            let nvmNpm = "\(nvmBase)/\(latest)/bin/npm"
            if FileManager.default.fileExists(atPath: nvmNpm) { return nvmNpm }
        }
        return candidates.first { FileManager.default.fileExists(atPath: $0) }
    }

    @discardableResult
    private static func run(_ executable: String, args: [String], env: [String: String]) -> Error? {
        let proc = Process()
        proc.executableURL = URL(fileURLWithPath: executable)
        proc.arguments = args
        proc.environment = env
        proc.standardOutput = FileHandle.nullDevice
        proc.standardError = FileHandle.nullDevice
        do {
            try proc.run()
            proc.waitUntilExit()
            guard proc.terminationStatus == 0 else {
                return CLIInstallerError.npmFailed(args.last ?? executable)
            }
        } catch {
            return error
        }
        return nil
    }
}
