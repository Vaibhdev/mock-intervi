# Interview Practice Partner

An AI-powered mock interview application designed to help users practice technical and behavioral interviews. The application uses Google's Gemini model to simulate a realistic interviewer, providing real-time voice interaction and comprehensive feedback.

## 🏗️ Architecture

The application follows a modular architecture separating the frontend UI from the core AI logic.

### Components

1.  **Frontend (`Manager.py`)**:
    *   Built with **Streamlit**.
    *   Handles the user interface, including the configuration page, live interview session, and feedback report.
    *   Manages application state (session state) for interview progress, audio status, and theme preferences.
    *   Implements a custom **Light/Dark mode** toggle using CSS variables and Streamlit's state.
    *   Handles audio input (microphone) using `speech_recognition` and output (TTS) using `pyttsx3`.

2.  **AI Logic (`agent.py`)**:
    *   Contains the `InterviewManager` class.
    *   Interacts with **Google Gemini API** (`gemini-2.5-flash`) to generate interview questions and feedback.
    *   Manages the conversation history and system prompts.
    *   Implements specific **Interview Protocols** (e.g., "The Thread Follower", "The Deep Diver") to ensure dynamic and relevant questioning.

3.  **Configuration**:
    *   Uses `.env` for secure API key management.
    *   `requirements.txt` for dependency management.

## 🎨 Design Decisions

*   **Dual-Theme UI**: A custom CSS implementation allows for a seamless switch between Light and Dark modes, ensuring accessibility and user preference support. The design uses a unified color palette system defined in `Manager.py`.
*   **Real-time Interaction**: The app prioritizes a "live" feel with an animated "Orb" visualizer and auto-submit functionality for speech, mimicking a real video call.
*   **Structured Interview Flow**:
    *   **Introduction**: Starts with a standard "Tell me about yourself".
    *   **The Pivot**: Dynamically adjusts based on the user's intro (e.g., digging into a specific tool mentioned).
    *   **Standard/Behavioral**: Proceeds with role-specific questions.
*   **Agentic Behavior**: The AI is instructed to follow specific protocols (e.g., "The Socratic Guide") to act more like a human interviewer rather than a simple Q&A bot.
*   **Comprehensive Feedback**: At the end of the session, the AI generates a structured JSON report evaluating Communication, Technical Knowledge, Strengths, and Areas for Improvement.

## 🚀 Setup Instructions

### Prerequisites

*   Python 3.8 or higher
*   A Google Gemini API Key

### Installation

1.  **Clone the repository** (if applicable) or download the source files.

2.  **Install Dependencies**:
    Navigate to the project directory and run:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: You may need to install system-level dependencies for `pyaudio` (e.g., `portaudio` on Mac/Linux) if you encounter issues.*

3.  **Configure Environment Variables**:
    Create a `.env` file in the root directory and add your Gemini API key:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```

### Running the Application

Execute the following command in your terminal:

```bash
streamlit run Manager.py
```

The application will open in your default web browser.

## 📂 File Structure

*   `Manager.py`: Main application entry point and UI logic.
*   `agent.py`: AI agent logic and Gemini API integration.
*   `requirements.txt`: Python dependencies.
*   `.env`: Environment variables (API keys).
