import psycopg2
from psycopg2 import sql, errors

# Config file
config = {
    'dbname': 'your_database_name',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost'
}

# Get the database name from the config
database_name = config['dbname']
html_file = f"{database_name}.html"

# Database Connection
try:
    conn = psycopg2.connect(**config)
    cursor = conn.cursor()
    print("Connection Successful")
except errors.OperationalError as err:
    print("Error connecting to the database:", err)
    exit()

# Create HTML header
html_header = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{database_name} Schema</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        @media (max-width: 600px) {{
            table {{
                display: block;
                overflow-x: auto;
                white-space: nowrap;
            }}
        }}
    </style>
</head>
<body>
    <h1>{database_name} Schema</h1>
"""

# Create HTML footer
html_footer = """
</body>
</html>
"""

# Database schema query and HTML content generation
try:
    # Fetch table names in ascending order
    cursor.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name ASC")
    tables = cursor.fetchall()

    with open(html_file, "w") as f:
        f.write(html_header)

        for table in tables:
            table_name = table[0]
            # Fetch column details in ascending order by column name
            cursor.execute(sql.SQL(
                "SELECT column_name, data_type, is_nullable, column_default, character_maximum_length FROM information_schema.columns WHERE table_name = %s ORDER BY column_name ASC"),
                [table_name])
            columns = cursor.fetchall()

            # Create HTML table with column information
            table_html = f"""
    <h2>{table_name}</h2>
    <table>
        <thead>
            <tr>
                <th>Column</th>
                <th>Type</th>
                <th>Null</th>
                <th>Default</th>
                <th>Max Length</th>
            </tr>
        </thead>
        <tbody>
"""
            for column in columns:
                table_html += "            <tr>\n"
                table_html += "                " + "".join(
                    f"<td>{x if x is not None else 'N/A'}</td>" for x in column) + "\n"
                table_html += "            </tr>\n"

            table_html += "        </tbody>\n    </table>\n"

            f.write(table_html)

        f.write(html_footer)

    print(f"HTML file '{html_file}' created successfully.")

except psycopg2.Error as err:
    print("Error querying the database:", err)
finally:
    # Close the DB connection
    cursor.close()
    conn.close()
