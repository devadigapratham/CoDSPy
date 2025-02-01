import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import dspy
import gradio as gr
from typing import Dict

# ======================
# DSPy Modules (Fixed ReAct Implementation)
# ======================

class CodeAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        # Define tools for ReAct
        self.tools = [
            dspy.Tool(name="code_analysis", func=self._analyze_code),
            dspy.Tool(name="suggestion_generator", func=self._generate_suggestions)
        ]
        self.analyze_code = dspy.ReAct("code -> issues, suggestions", tools=self.tools)
    
    def _analyze_code(self, code: str) -> str:
        """Tool for analyzing code issues"""
        return f"Analyzing code for potential issues..."
    
    def _generate_suggestions(self, issues: str) -> str:
        """Tool for generating suggestions"""
        return f"Generating optimization suggestions based on issues..."
    
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
        # Define tools for ReAct
        self.tools = [
            dspy.Tool(name="code_optimizer", func=self._optimize_code),
            dspy.Tool(name="code_refactor", func=self._refactor_code)
        ]
        self.optimize_code = dspy.ReAct("code, suggestions -> optimized_code", tools=self.tools)
    
    def _optimize_code(self, code: str) -> str:
        """Tool for code optimization"""
        return f"Optimizing code structure..."
    
    def _refactor_code(self, code: str) -> str:
        """Tool for code refactoring"""
        return f"Refactoring code for better readability..."
    
    def optimize(self, code: str, suggestions: str) -> str:
        try:
            prediction = self.optimize_code(code=code, suggestions=suggestions)
            return prediction.optimized_code
        except Exception as e:
            return f"Optimization error: {str(e)}"

class TestGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        # Define tools for ReAct
        self.tools = [
            dspy.Tool(name="test_case_generator", func=self._generate_test_cases),
            dspy.Tool(name="test_code_writer", func=self._write_test_code)
        ]
        self.generate_tests = dspy.ReAct("code -> test_cases, test_code", tools=self.tools)
    
    def _generate_test_cases(self, code: str) -> str:
        """Tool for generating test cases"""
        return f"Generating test cases..."
    
    def _write_test_code(self, test_cases: str) -> str:
        """Tool for writing test code"""
        return f"Writing test code implementation..."
    
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
# Core System (Unchanged)
# ======================

class CodeForge:
    def __init__(self):
        dspy.configure(lm=dspy.OllamaLocal(model='llama3.2:3b', device='cuda', temperature=0.2))
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
