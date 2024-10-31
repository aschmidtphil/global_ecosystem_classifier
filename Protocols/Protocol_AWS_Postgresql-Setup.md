# Steps to Create a PostgreSQL DB Instance on AWS and Configure Security Groups

---

## Step 1: Log in to AWS Management Console
- Open [AWS Management Console](https://aws.amazon.com/console/).
- Log in using your AWS credentials.

---

## Step 2: Navigate to RDS Service
- Search for **RDS** and select **Amazon RDS**.
- Use RDS to set up a managed PostgreSQL instance.

---

## Step 3: Create a New Database Instance
1. Click **Create database**.
2. **Database Creation Method**: Choose **Standard Create**.
3. **Engine Options**: Select **PostgreSQL**.
4. **Version**: Choose your preferred PostgreSQL version.

---

## Step 4: Configure Database Settings
| **Setting**               | **Description**                                |
|---------------------------|------------------------------------------------|
| **DB Instance Type**      | Choose **Production** or **Dev/Test**.         |
| **Templates**             | Select **Free Tier**, **Single-AZ**, or **Multi-AZ**. |
| **DB Instance Identifier**| Unique name, e.g., `my-postgres-db`.           |
| **Master Username**       | Set your username.                             |
| **Master Password**       | Enter and confirm your password.               |

---

## Step 5: Choose Instance Specifications
| **Specification**         | **Details**                                    |
|---------------------------|------------------------------------------------|
| **DB Instance Class**     | Instance size, e.g., `db.t3.micro` or `db.m5.large`. |
| **Storage**               | Allocated storage, e.g., 20 GB. Enable **autoscaling** if needed. |

---

## Step 6: Configure Connectivity
| **Setting**               | **Details**                                    |
|---------------------------|------------------------------------------------|
| **VPC**                   | Select your VPC.                               |
| **Subnet Group**          | Choose a subnet group.                         |
| **Public Access**         | Select **Yes** or **No**.                      |
| **VPC Security Group**    | Choose or create a security group.             |

---

## Step 7: Configure Security Groups
1. **Create a New Security Group**:
   - Navigate to **VPC > Security Groups** and click **Create Security Group**.
   - Provide a **Name** and **Description**.
   - **Inbound Rules**:
     - Click **Edit Inbound Rules**.
     - **Type**: PostgreSQL (port **5432**).
     - **Source**: Use **My IP** or specify a custom range (e.g., `0.0.0.0/0` for open access; not recommended for production).
   - **Outbound Rules**: Allow all traffic by default.
   - Click **Create**.

2. **Attach Security Group**:
   - Return to RDS and select the new security group.

---

## Step 8: Configure Additional Settings
| **Setting**               | **Description**                                |
|---------------------------|------------------------------------------------|
| **Database Options**      | Provide a **Database Name** if needed.         |
| **Backup**                | Enable and specify the **retention period**.   |
| **Encryption**            | Enable for security in production.             |

---

## Step 9: Finalize and Create the DB Instance
- Review settings and click **Create Database**.
- Wait for AWS to provision the instance.

---

## Step 10: Connect to Your PostgreSQL Instance
1. **Get Connection Details**:
   - Find **Endpoint** and **Port** in the **Connectivity & Security** section.
2. **Connect Using psql**:
   ```sh
   psql -h <endpoint> -U <master_username> -d <database_name> -p 5432
