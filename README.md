## Technical Debt Analyzer

### How to run the application:

1. Navigate to the ```web``` folder
2. Add a ```.env``` file with your Github token (Based on the .env.example)
3. Navigate to the root of the project
4. ```sudo docker compose build```
5. ```sudo docker compose up -d```
6. Go to localhost in your browser
7. To disable application type ```docker compose down```

### How to generate a Github token

1. Open the following url ```https://github.com/settings/tokens```
2. Generate a new token (classic)
3. Give full repo access to the token
4. Generate the token
5. Copy the token to the .env file

## Class Diagram

```mermaid
classDiagram
		class Repository {
			+id: string(36)
			+owner: text
			+name: text
		}

		class Branch {
			+id: string(36)
			+repository_id: string(36)
			+name: text
		}

		class Commit {
			+id: string(36)
			+branch_id: string(36)
			+sha: text
			+date: datetime
		}

		class File {
			+id: string(36)
			+commit_id: string(36)
			+name: text
		}

		class Function {
			+id: string(36)
			+file_id: string(36)
			+name: text
			+line_position: int
		}

		class Complexity {
			+id: string(36)
			+function_id: string(36)
			+value: int
		}

		class Coverage {
			+id: string(36)
			+function_id: string(36)
			+value: int
		}

		class Size {
			+id: string(36)
			+function_id: string(36)
			+value: int
		}

		class FileTestCoverage {
			+id: string(36)
			+file_id: string(36)
			+value: int
		}

		class FunctionTestCoverage {
			+id: string(36)
			+function_id: string(36)
			+value: int
		}

		class Tests {
			+id: string(36)
			+passing_test_number: int
			+failing_test_number: int
		}

		class FileEntities {
			+id: string(36)
			+identifiable_entity_id: string(36)
			+file_id: string(36)
			+line_position: int
		}

		class IdentifableEntity {
			+id: string(36)
			+name: text
		}

		Branch --> Repository : repository_id
		Commit --> Branch : branch_id
		File --> Commit : commit_id
		Function --> File : file_id
		Complexity --> Function : function_id
		Coverage --> Function : function_id
		Size --> Function : function_id
		FileTestCoverage --> File : file_id
		FunctionTestCoverage --> Function : function_id
		Tests --> Branch
		FileEntities --> File : file_id
		FileEntities --> IdentifableEntity : identifiable_entity_id
```
