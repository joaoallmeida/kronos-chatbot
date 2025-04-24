from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders.parsers import RapidOCRBlobParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant.vectorstores import Qdrant
from utils import *

class Document:

    def pdf_load(self):
        try:

            file = st.session_state.uploaded_file
            file_path = f"/tmp/{file.name}"
            file_type = file.type.split('/')[1]

            with st.spinner(f'Processando Arquivo: {file.name}...'):
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())

                loader = PyMuPDFLoader(
                    file_path,
                    mode='page',
                    extract_images=True,
                    images_inner_format="markdown-img",
                    images_parser=RapidOCRBlobParser(),
                )
                documents =  loader.load()

                # Add source metadata
                for doc in documents:
                    doc.metadata.update({
                        "source_type": file_type,
                        "file_name": file.name,
                        "timestamp": datetime.now().isoformat()
                    })

                text_splitter = RecursiveCharacterTextSplitter( chunk_size=2048, chunk_overlap=128 )
                docs = text_splitter.split_documents(documents)

                embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
                vector_stores = Qdrant.from_documents(docs, embeddings, location=":memory:", collection_name="document_embeddings")

                st.success(f"Arquivo processado", icon='✅')

        except Exception as e:
            raise e

        return vector_stores.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": 5, "score_threshold": st.session_state.threshold}
            )