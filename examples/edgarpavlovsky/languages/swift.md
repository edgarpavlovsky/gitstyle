---
title: "Swift Idioms"
category: language
confidence: medium
sources: [edgarpavlovsky/yc-demo-day-countdown]
related: [naming-conventions, patterns, type-discipline]
last_updated: 2026-04-07
---

# Swift Idioms

## SwiftUI Patterns

The developer uses modern SwiftUI idioms:

- View composition with small, reusable components
- `@State` for local state, `@Binding` for passed state
- `@ObservableObject` for shared data models
- Preview providers included for visual development [a4c2e8f](https://github.com/edgarpavlovsky/yc-demo-day-countdown/commit/a4c2e8f)

```swift
struct CountdownView: View {
    @State private var daysRemaining: Int = 0
    let targetDate: Date
    
    var body: some View {
        VStack {
            Text("\(daysRemaining)")
                .font(.system(size: 72, weight: .bold))
            Text("days remaining")
                .foregroundColor(.secondary)
        }
        .onAppear { updateCountdown() }
    }
}
```

## Value Types

Strong preference for `struct` over `class`. Classes are reserved for cases requiring reference semantics (e.g., `ObservableObject` conformance).

## Error Handling

Uses Swift's native error handling (`throws`, `try`, `catch`) rather than Result types or completion handlers. With async/await available, the developer migrates toward structured concurrency.

## Closures

Trailing closure syntax used consistently. In short closures, `$0`/`$1` shorthand is used; longer closures use named parameters for clarity.
