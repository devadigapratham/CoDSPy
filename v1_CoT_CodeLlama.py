import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import dspy
import gradio as gr
from typing import Dict

# ======================
# DSPy Modules
# ======================

class CodeAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyze_code = dspy.ChainOfThought("code -> issues, suggestions")
    
    def analyze(self, code: str) -> Dict[str, str]:
        try:
            prediction = self.analyze_code(code=code)
            return {
                "issues": prediction.issues,
                "suggestions": prediction.suggestions
            }
        except Exception as e:
            return {
                "issues": f"Analysis error: {str(e)}",
                "suggestions": "No suggestions available"
            }

class CodeOptimizer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.optimize_code = dspy.ChainOfThought("code, suggestions -> optimized_code")
    
    def optimize(self, code: str, suggestions: str) -> str:
        try:
            prediction = self.optimize_code(code=code, suggestions=suggestions)
            return prediction.optimized_code
        except Exception as e:
            return f"Optimization error: {str(e)}"

class TestGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_tests = dspy.ChainOfThought("code -> test_cases, test_code")
    
    def create_tests(self, code: str) -> Dict[str, str]:
        try:
            prediction = self.generate_tests(code=code)
            return {
                "test_cases": prediction.test_cases,
                "test_code": prediction.test_code
            }
        except Exception as e:
            return {
                "test_cases": f"Test generation failed: {str(e)}",
                "test_code": "Unable to generate test code"
            }

# ======================
# Core System
# ======================

class CodeForge:
    def __init__(self):
        dspy.configure(lm=dspy.OllamaLocal(model='codellama:7b', device='cuda', temperature=0.2))
        self.analyzer = CodeAnalyzer()
        self.optimizer = CodeOptimizer()
        self.tester = TestGenerator()
    
    def process(self, code: str) -> Dict[str, str]:
        analysis = self.analyzer.analyze(code)
        optimized = self.optimizer.optimize(code, analysis["suggestions"])
        tests = self.tester.create_tests(code)
        
        return {
            "issues": analysis["issues"],
            "suggestions": analysis["suggestions"],
            "optimized_code": optimized,
            "test_cases": tests["test_cases"],
            "test_code": tests["test_code"]
        }

# ======================
# Gradio Interface
# ======================

def create_interface():
    forge = CodeForge()
    
    with gr.Blocks(theme=gr.themes.Soft(), title="CodeForge AI") as app:
        gr.Markdown("# CoDSPy - AI Code Optimizer & Test Generator")
        
        with gr.Row():
            with gr.Column():
                input_code = gr.Code(
                    label="Input Python Code",
                    language="python",
                    lines=15,
                    elem_id="input-code"
                )
                process_btn = gr.Button("Analyze & Improve", variant="primary")
            
            with gr.Column():
                with gr.Tabs():
                    with gr.Tab("Analysis"):
                        issues_out = gr.Textbox(label="Detected Issues", interactive=False, lines=3)
                        suggestions_out = gr.Textbox(label="Optimization Suggestions", lines=5, interactive=False)
                    
                    with gr.Tab("Optimized Code"):
                        optimized_code_out = gr.Code(
                            label="Improved Code",
                            language="python",
                            lines=15,
                            interactive=False
                        )
                    
                    with gr.Tab("Tests"):
                        test_cases_out = gr.Textbox(label="Suggested Test Cases", lines=4, interactive=False)
                        test_code_out = gr.Code(
                            label="Generated Test Code",
                            language="python",
                            lines=15,
                            interactive=False
                        )

        @process_btn.click(
            inputs=[input_code],
            outputs=[issues_out, suggestions_out, optimized_code_out, test_cases_out, test_code_out]
        )
        def process_code(code):
            if not code.strip():
                raise gr.Error("Please input some code to analyze!")
            
            results = forge.process(code)
            return (
                results["issues"],
                results["suggestions"],
                results["optimized_code"],
                results["test_cases"],
                results["test_code"]
            )

    return app

if __name__ == "__main__":
    web_app = create_interface()
    web_app.launch(server_port=7860, server_name="0.0.0.0")