# Multiple Choice Questions - Machine Learning Supervised Learning
mcq = [
    {
        "question": r"""Which of the following best describes the bias-variance tradeoff in machine learning?""",
        "options": [
            r"High bias models always perform better than high variance models",
            r"Bias and variance are independent and don't affect each other", 
            r"Reducing bias typically increases variance, and vice versa",
            r"Variance only matters in unsupervised learning",
            r"Bias and variance can both be minimized simultaneously without any tradeoff"
        ],
        "answer": r"Reducing bias typically increases variance, and vice versa",
        "marks": 2
    },
    {
        "question": r"""In a decision tree, which impurity measure is most commonly used for classification tasks?""",
        "options": [
            r"Mean Squared Error (MSE)",
            r"Gini Impurity", 
            r"Mean Absolute Error (MAE)",
            r"R-squared",
            r"Cross-entropy",
            r"Pearson correlation"
        ],
        "answer": r"Gini Impurity",
        "marks": 2
    }
]

# Subjective Questions with templated variants - Machine Learning
subjective = [
    {
        "question": r"""Compare and contrast the following three supervised learning algorithms in terms of their assumptions, strengths, and weaknesses: Linear Regression, Decision Trees, and k-NN. Fill in a comparison table and provide a brief explanation for each entry.""",
        "answer": r"Linear: Linear relationship, normality | Interpretable, fast | Limited to linear patterns. Trees: No assumptions | Interpretable, handles non-linear | Prone to overfitting. k-NN: Locality assumption | Simple, non-parametric | Computationally expensive, curse of dimensionality",
        "marks": 9
    },
    {
        "template": r"""Consider the following dataset for linear regression:

\begin{center}
\begin{tabular}{|c|c|c|c|}
\hline
\textbf{Sample} & \textbf{Feature 1} & \textbf{Feature 2} & \textbf{Target} \\
\hline
1 & {{ x1_1 }} & {{ x2_1 }} & {{ y1 }} \\
\hline
2 & {{ x1_2 }} & {{ x2_2 }} & {{ y2 }} \\
\hline
3 & {{ x1_3 }} & {{ x2_3 }} & {{ y3 }} \\
\hline
4 & {{ x1_4 }} & {{ x2_4 }} & {{ y4 }} \\
\hline
\end{tabular}
\end{center}

\textbf{a)} Calculate the mean squared error (MSE) if the model predicts $\hat{y} = {{ pred1 }}, {{ pred2 }}, {{ pred3 }}, {{ pred4 }}$ respectively. \textbf{[3 marks]}

\textbf{b)} If we use L2 regularization with $\lambda = {{ lambda_val }}$, write the complete loss function. \textbf{[2 marks]}""",
        "variables": [
            {
                "x1_1": 2, "x2_1": 1, "y1": 5, "x1_2": 4, "x2_2": 3, "y2": 11, 
                "x1_3": 1, "x2_3": 2, "y3": 4, "x1_4": 3, "x2_4": 4, "y4": 10,
                "pred1": 4.8, "pred2": 10.5, "pred3": 4.2, "pred4": 9.8,
                "lambda_val": 0.01,
                "answer": "a) MSE = 0.1425, b) Loss = MSE + 0.01 * Σ(wi²)"
            },
            {
                "x1_1": 1, "x2_1": 2, "y1": 6, "x1_2": 3, "x2_2": 1, "y2": 7, 
                "x1_3": 2, "x2_3": 3, "y3": 9, "x1_4": 4, "x2_4": 2, "y4": 10,
                "pred1": 5.9, "pred2": 7.1, "pred3": 8.8, "pred4": 9.9,
                "lambda_val": 0.05,
                "answer": "a) MSE = 0.0175, b) Loss = MSE + 0.05 * Σ(wi²)"
            }
        ],
        "marks": 5
    }
]