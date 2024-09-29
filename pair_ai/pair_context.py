

from pydantic import BaseModel, Field
from openai_models import ChatCompletionMessage
from typing import List
import mimetypes

class FileContent(BaseModel):
    filename:  str
    content:   str

    def messages(self) -> List[ChatCompletionMessage]:
        content = f"filename: {self.filename}\n{self.content}"
        return [ChatCompletionMessage(role='user', content=content)]


    
class PairContext(BaseModel):

    project_files : str                             # list of filenames in the project directory
    file_contents : List[FileContent]    
    chat_messages : List[ChatCompletionMessage]

    def messages(self) -> List[ChatCompletionMessage]:

        BASE_PROMPT =  "You are a programming assistant. "
        BASE_PROMPT += "Below are portions of code the user is working on as well as questions from the user. "
        BASE_PROMPT += "Provide helpful answers to the user. If you need more information on code that is not included, "
        BASE_PROMPT += "ask for the contents of the code file. "
        BASE_PROMPT += "Add comments in the code around the code we are changing. Document the user-supplied requirements in the code.  "
        BASE_PROMPT += "When generating example code that takes an input file, arrange the main code to take the filename as a command line argument. "
        BASE_PROMPT += "When outputing code blocks, please include the filepath/filename as shown below.  Do not include any text in the code block header other than the filename. "
        BASE_PROMPT += "When making changes to existing files, be sure to output the full file content without skipping any parts. "        
        BASE_PROMPT += "Do not remove any existing comments, copy them as-is. "


        messages  = [ChatCompletionMessage(role='user', content=BASE_PROMPT)]

        example_codeblock = "This is the code block format we are using:  \n  \n"
        example_codeblock += "**hello.py**\n```python\nprint('hello world')\n```\n"
        messages  += [ChatCompletionMessage(role='user', content=example_codeblock)]

        
        # introduce the project files
        if self.project_files:
            filesprompt = "Here is a listing all files in our project directory: \n"
            filesprompt += self.project_files        
            messages  += [ChatCompletionMessage(role='user', content=filesprompt)]

        # introduce the file contents
        file_intro = "Here are the current contents of some of the files to help completing the task. "
        
        # add the file contents
        messages  += [ChatCompletionMessage(role='user', content=file_intro)]
        for f in self.file_contents:
            messages += f.messages()

        # add the chat messages to the end
        return messages + self.chat_messages


        
class FilesContext(BaseModel):
    project_files : str      # list of filenames in the project directory
    file_contents : List[FileContent]    
    chat_messages : List[ChatCompletionMessage]

    def messages(self) -> List[ChatCompletionMessage]:

        BASE_PROMPT =  "You are a programming assistant. "
         
        messages  = [ChatCompletionMessage(role='user', content=BASE_PROMPT)]

        # introduce the project files
        filesprompt = "Here is a listing all files in our project directory: \n"
        filesprompt += self.project_files
        
        messages  += [ChatCompletionMessage(role='user', content=filesprompt)]

        # introduce the file contents
        file_intro = "Here are some files contents we are already looking at. "
        
        # add the file contents
        messages  += [ChatCompletionMessage(role='user', content=file_intro)]
        for f in self.file_contents:
            messages += f.messages()
            
        query = "Which of the existing files do we need to read, reference, or edit for this task?"
        messages  += [ChatCompletionMessage(role='user', content=query)]
        
        # add the chat messages to the end
        return messages + self.chat_messages[-3:]





class FileList(BaseModel):
    filenames: List[str] = Field(description = 'A filename that needs to be read or edited in order to respond to the user.')
