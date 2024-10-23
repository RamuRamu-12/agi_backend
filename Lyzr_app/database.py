import psycopg2

class PostgreSQLDB:
    def __init__(self, dbname, user, password, host='cornelius.db.elephantsql.com', port=5432):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connect(self):
        try:
            conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            return conn
        except Exception as e:
            print(e)
            return None

    #Environmment Table creation
    # Environment Table creation with removed columns
    def table_creation(self):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = """
                CREATE TABLE IF NOT EXISTS environment (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    api_key TEXT NOT NULL,
                    model VARCHAR(100) NOT NULL,
                    temperature NUMERIC(3, 2) DEFAULT 0.5
                );
                """
                cursor.execute(query)
                conn.commit()
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error creating environment table: {e}")

    # Table deletion for environment
    def table_deletion(self):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = "DROP TABLE IF EXISTS environment CASCADE;"
                cursor.execute(query)
                conn.commit()
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error deleting environment table: {e}")

    # Create Environment without top_p and model_vendor
    def create_environment(self, name, api_key, model, temperature=0.5):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = """
                INSERT INTO environment (name, api_key, model, temperature)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """
                cursor.execute(query, (name, api_key, model, temperature))
                environment_id = cursor.fetchone()[0]
                conn.commit()
                cursor.close()
                conn.close()
                print(f"Environment added with ID: {environment_id}")
                return environment_id
        except Exception as e:
            print(f"Error creating environment: {e}")
            return None

    # Read environment by ID
    def read_environment(self, environment_id):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = "SELECT * FROM environment WHERE id = %s;"
                cursor.execute(query, (environment_id,))
                environment = cursor.fetchone()
                cursor.close()
                conn.close()
                if environment:
                    print(f"Environment found: {environment}")
                    return environment
                else:
                    print(f"No environment found with ID: {environment_id}")
                    return None
        except Exception as e:
            print(f"Error reading environment: {e}")
            return None

    # Update environment without top_p and model_vendor
    def update_environment(self, environment_id, name=None, api_key=None, model=None, temperature=None):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = """
                UPDATE environment
                SET name = COALESCE(%s, name),
                    api_key = COALESCE(%s, api_key),
                    model = COALESCE(%s, model),
                    temperature = COALESCE(%s, temperature)
                WHERE id = %s;
                """
                cursor.execute(query, (name, api_key, model, temperature, environment_id))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"Environment with ID {environment_id} updated.")
        except Exception as e:
            print(f"Error updating environment: {e}")

    # Delete environment by ID
    def delete_environment(self, environment_id):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = "DELETE FROM environment WHERE id = %s;"
                cursor.execute(query, (environment_id,))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"Environment with ID {environment_id} deleted.")
        except Exception as e:
            print(f"Error deleting environment: {e}")

    # Read all environments without top_p and model_vendor
    def read_all_environments(self):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = "SELECT * FROM environment;"
                cursor.execute(query)
                environments = cursor.fetchall()
                cursor.close()
                conn.close()
                if environments:
                    for environment in environments:
                        print(
                            f"ID: {environment[0]}, Name: {environment[1]}, Model: {environment[3]}, Temperature: {environment[4]}")
                    return environments
                else:
                    print("No environments found.")
                    return None
        except Exception as e:
            print(f"Error reading all environments: {e}")
            return None

    #Agents table
    # Create agents table linked with environments, including 'tools' column
    def create_agents_table(self):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = """
                CREATE TABLE IF NOT EXISTS agents (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    system_prompt TEXT,
                    agent_description TEXT,
                    tools TEXT,  -- Tools used by the agent
                    upload_attachment BOOLEAN DEFAULT FALSE,  
                    env_id INT REFERENCES environment(id) ON DELETE CASCADE
                );
                """
                cursor.execute(query)
                conn.commit()
                cursor.close()
                conn.close()
                print("Agents table created successfully.")
        except Exception as e:
            print(f"Error creating agents table: {e}")

    # Drop agents table
    def drop_agents_table(self):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = "DROP TABLE IF EXISTS agents;"
                cursor.execute(query)
                conn.commit()
                cursor.close()
                conn.close()
                print("Agents table deleted.")
        except Exception as e:
            print(f"Error deleting agents table: {e}")


    # Insert a new agent, including 'tools'
    # Insert a new agent, including 'upload_attachment'
    def create_agent(self, name, system_prompt, agent_description, tools, upload_attachment, env_id):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = """
                INSERT INTO agents (name, system_prompt, agent_description, tools, upload_attachment, env_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """
                cursor.execute(query, (name, system_prompt, agent_description, tools, upload_attachment, env_id))
                agent_id = cursor.fetchone()[0]  # Expecting a single row with the new agent ID
                conn.commit()
                cursor.close()
                conn.close()
                return agent_id
        except Exception as e:
            print(f"Error creating agent: {e}")
            return None

    # Read agent by ID
    def read_agent(self, agent_id):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = "SELECT * FROM agents WHERE id = %s;"
                cursor.execute(query, (agent_id,))
                agent = cursor.fetchone()
                cursor.close()
                conn.close()
                return agent
        except Exception as e:
            print(f"Error reading agent: {e}")
            return None

    # Update agent, including 'tools'
    def update_agent(self, agent_id, name=None, system_prompt=None, agent_description=None, tools=None,
                     upload_attachment=None, env_id=None):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = """
                UPDATE agents
                SET name = COALESCE(%s, name),
                    system_prompt = COALESCE(%s, system_prompt),
                    agent_description = COALESCE(%s, agent_description),
                    tools = COALESCE(%s, tools),
                    upload_attachment = COALESCE(%s, upload_attachment),
                    env_id = COALESCE(%s, env_id)
                WHERE id = %s;
                """
                cursor.execute(query, (
                name, system_prompt, agent_description, tools, upload_attachment, env_id, agent_id))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"Agent with ID {agent_id} updated.")
        except Exception as e:
            print(f"Error updating agent: {e}")

    # Delete agent by ID
    def delete_agent(self, agent_id):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = "DELETE FROM agents WHERE id = %s;"
                cursor.execute(query, (agent_id,))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"Agent with ID {agent_id} deleted.")
        except Exception as e:
            print(f"Error deleting agent: {e}")

    # Get all agents, including 'tools'
    def get_all_agents(self):
        try:
            conn = self.connect()
            if conn is not None:
                cursor = conn.cursor()
                query = """
                SELECT id, name, system_prompt, agent_description, tools, upload_attachment, env_id 
                FROM agents;
                """
                cursor.execute(query)
                agents = cursor.fetchall()
                cursor.close()
                conn.close()
                return agents
        except Exception as e:
            print(f"Error retrieving agents: {e}")
            return None


if __name__ == "__main__":
    db = PostgreSQLDB(dbname='uibmogli', user='uibmogli', password='8ogImHfL_1G249lXtM3k2EAIWTRDH2mX')
    db.table_creation()
    db.create_agents_table()
    #db.read_environment(1)
    #db.table_deletion()
    #db.drop_agents_table()
