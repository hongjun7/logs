---
title: 'Competitive Programming with Rust'
tags: Rust
---

[Competitive Programming](https://en.wikipedia.org/wiki/Competitive_programming) demands a strong understanding of algorithms, data structures, and the ability to code swiftly. [Rust](https://www.rust-lang.org/), with its safety features and high-performance capabilities, is a good choice for competitive programming.
This post introduces the advantages of Rust and provides insights into useful tools for competitions.

## Advantages of Rust

#### 1. Safety and Reliability
Rust boasts a powerful type system that [guarantees memory safety](https://stanford-cs242.github.io/f18/lectures/05-1-rust-memory-safety.html). This prevents runtime errors, making it easier to write secure code.

#### 2. Good Performance
Rust's performance rivals that of C and C++, a crucial factor when competing against time constraints. This advantage becomes evident when implementing complex algorithms or handling large datasets.

#### 3. Libraries and Tools
[rust-competitive-helper](https://github.com/rust-competitive-helper) provides tools and templates tailored for competitive programming. [example-contests-workspace](https://github.com/rust-competitive-helper/example-contests-workspace) simplifies the process of setting up a contest environment.
Utilize [EgorKulikov/rust_algo](https://github.com/EgorKulikov/rust_algo) and [EbTech/rust-algorithms](https://github.com/EbTech/rust-algorithms) for a collection of data structures and algorithms. These libraries enable rapid implementation during competitions.

## Getting Started with Rust

#### 1. Installing Rust and IDE
  - Begin by installing Rust from the [official website](https://www.rust-lang.org/tools/install).
  - Choose the installation method suitable for your platform.
  - [Jetbrains:RustRover](https://www.jetbrains.com/rust/) is a powerful IDE for Rust. Install this from the official website.
    <p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_assets/2023-09-30-rust-cp-helper/rust_preview.gif?raw=true"> </p>

#### 2. Installing [rust-competitive-helper](https://github.com/rust-competitive-helper)
  - Switch default rust toolchain to nightly:
    ```shell
    $ rustup default nightly
    ```
  - Install `rust-competitive-helper` binary:
    ```shell
    $ cargo install --git https://github.com/rust-competitive-helper/rust-competitive-helper
    ```
  - Fork [rust-competitive-helper](https://github.com/rust-competitive-helper/rust-competitive-helper) repository on github, clone it locally
  - Fork [example-contests-workspace](https://github.com/rust-competitive-helper/example-contests-workspace) repository on github, clone it locally, open in [RustRover](https://www.jetbrains.com/rust/)
  - In [RustRover](https://www.jetbrains.com/rust/) terminal, run `rust-competitive-helper` from current directory
    - Linux
      ```shell
      $ ./rust-competitive-helper
      ``` 
    - Windows
      ```shell
      $ start rust-competitive-helper
      ```
    If it has operated correctly, an executable program will run.

#### 3. To use with [competitive-companion](https://github.com/jmerle/competitive-companion):
  - Add 4244 to custom ports in plugin
  - Choose `Run listener` in `rust-competitive-helper`
  - Click `Parse task` in plugin
  - Project for this task will be created and opened in [RustRover](https://www.jetbrains.com/rust/)
  - Testing should be done by running `main.rs` in corresponding crate
  - Submit `./main/src/main.rs`

Following the instructions provided above, you have completed the basic setup for solving problems in Rust.
If you're curious about the additional data structures and algorithms set up in `example-contests-workspace`, refer to [EgorKulikov/rust_algo](https://github.com/EgorKulikov/rust_algo) or [hongjun7/cp-rust](https://github.com/hongjun7/cp-rust).

## Useful resource for learning Rust
- ["A half-hour to learn Rust" by fasterthanli](https://fasterthanli.me/articles/a-half-hour-to-learn-rust)
- ["The Rust Book" by Steve Klabnik and Carol Nichols](https://doc.rust-lang.org/book/)
- [Rust By Example](https://doc.rust-lang.org/stable/rust-by-example/)
- [Read Rust](https://readrust.net/)
- [This Week In Rust](https://this-week-in-rust.org/)