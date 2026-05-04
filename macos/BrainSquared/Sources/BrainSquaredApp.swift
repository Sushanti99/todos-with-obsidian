import SwiftUI

@main
struct BrainSquaredApp: App {
    @StateObject private var serverManager = ServerManager()
    @AppStorage("vaultPath") private var vaultPath: String = ""
    @AppStorage("hasCompletedOnboarding") private var hasCompletedOnboarding: Bool = false

    var body: some Scene {
        WindowGroup {
            if hasCompletedOnboarding && !vaultPath.isEmpty {
                ContentView()
                    .environmentObject(serverManager)
                    .onAppear {
                        serverManager.start(vaultPath: vaultPath)
                    }
            } else {
                OnboardingView { completedVaultPath in
                    vaultPath = completedVaultPath
                    hasCompletedOnboarding = true
                    serverManager.start(vaultPath: completedVaultPath)
                }
            }
        }
        .windowStyle(.hiddenTitleBar)
        .windowResizability(.contentSize)
        .commands {
            CommandGroup(replacing: .newItem) {}
        }
    }
}
