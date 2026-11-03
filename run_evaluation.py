from rag.vector_store import VectorStore
from rag.retriever import Retriever
from fact_checker.fact_checker import FactChecker
from evaluation.evaluator import Evaluator, print_summary

EMBEDDING_DIM = 384
INDEX_FOLDER = "Data/index"

store = VectorStore.load(INDEX_FOLDER, EMBEDDING_DIM)
retriever = Retriever(store)
checker = FactChecker(retriever, k=3)

evaluator = Evaluator(checker)
report = evaluator.run()
print_summary(report)