require('dotenv').config();
const express = require('express');
const mysql = require('mysql2');
const bcrypt = require('bcrypt');
const session = require('express-session');
const MySQLStore = require('express-mysql-session')(session);
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

// -----------------------------
// Middleware
// -----------------------------
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files (HTML, CSS, JS)
app.use(express.static(path.join(__dirname, 'public')));

// -----------------------------
// Database Connection
// -----------------------------
const db = mysql.createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASS,
    database: process.env.DB_NAME,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
}).promise();

// -----------------------------
// Session
// -----------------------------
const sessionStore = new MySQLStore({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASS,
    database: process.env.DB_NAME
});

app.use(session({
    key: 'gopreach_session',
    secret: process.env.SESSION_SECRET,
    store: sessionStore,
    resave: false,
    saveUninitialized: false,
    cookie: { maxAge: 86400000, httpOnly: true }
}));

// -----------------------------
// Serve index.html for /
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// -----------------------------
// Handle Registration (POST /auth/register)
app.post('/auth/register', async (req, res) => {
    try {
        const { full_name, phone, email, batch, experience, language, password } = req.body;

        // Check if user exists
        const [existing] = await db.query('SELECT * FROM users WHERE email = ?', [email]);
        if (existing.length > 0) {
            return res.status(400).json({ message: 'Email already exists!' });
        }

        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Insert user
        const [result] = await db.query(
            'INSERT INTO users (full_name, phone, email, batch, experience, language, password) VALUES (?, ?, ?, ?, ?, ?, ?)',
            [full_name, phone, email, batch, experience, language, hashedPassword]
        );

        // ✅ Set session AFTER registration
        req.session.userId = result.insertId; // store the user id
        req.session.email = email;             // optional: store email

        // Respond
        res.status(201).json({ message: 'User registered successfully!' });

    } catch (err) {
        console.error(err);
        res.status(500).json({ message: 'Server error!' });
    }
});


app.post('/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        const [users] = await db.query('SELECT * FROM users WHERE email = ?', [email]);
        if (users.length === 0) {
            return res.status(400).json({ message: 'Email not found!' });
        }

        const user = users[0];
        const match = await bcrypt.compare(password, user.password);
        if (!match) {
            return res.status(400).json({ message: 'Incorrect password!' });
        }

        req.session.userId = user.id;
        req.session.email = user.email;

        res.status(200).json({ message: 'Login successful!' });

    } catch (err) {
        console.error(err);
        res.status(500).json({ message: 'Server error!' });
    }
});


// Middleware to check if user is logged in
function isAuth(req, res, next) {
    if (req.session.userId) {
        next(); // user is logged in, continue
    } else {
        res.redirect('/login.html'); // redirect to login if not logged in
    }
}

app.get('/dashboard', isAuth, (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'userdashboard.html'));
});

app.get('/adminpanel', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'adminlogin.html'));
});



app.post('/auth/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) {
            return res.status(500).json({ message: 'Logout failed!' });
        }
        res.clearCookie('gopreach_session');
        res.json({ message: 'Logged out successfully!' });
    });
});






// Get logged-in user info
app.get('/auth/user', async (req, res) => {
    if (!req.session.userId) {
        return res.status(401).json({ message: 'Not logged in' });
    }

    try {
        const [rows] = await db.query('SELECT full_name, email, notifications FROM users WHERE id = ?', [req.session.userId]);
        if (rows.length === 0) {
            return res.status(404).json({ message: 'User not found' });
        }

        const user = rows[0];

        // Get initials from full_name
        const initials = user.full_name.split(' ').map(n => n[0]).join('').toUpperCase();

        res.json({
            full_name: user.full_name,
            initials: initials,
            email: user.email,
            notifications: user.notifications || 0
        });

    } catch (err) {
        console.error(err);
        res.status(500).json({ message: 'Server error' });
    }
});


// GET user info
app.get("/auth/user2", async (req, res) => {
    try {
        if (!req.session.userId) {
            return res.status(401).json({ message: "Not logged in" });
        }

        const [rows] = await db.query(
            "SELECT id, full_name, email, phone, location FROM users WHERE id = ?",
            [req.session.userId]
        );

        if (rows.length === 0) {
            return res.status(404).json({ message: "User not found" });
        }

        const user = rows[0];

        // Generate initials from full_name
        let initials = "";
        if (user.full_name) {
            const parts = user.full_name.trim().split(" ");
            initials =
                (parts[0]?.charAt(0) || "") +
                (parts[1]?.charAt(0) || "");
            initials = initials.toUpperCase();
        }

        res.json({
            id: user.id,
            full_name: user.full_name,
            email: user.email,
            phone: user.phone,
            location: user.location,
            initials
        });

    } catch (err) {
        console.log(err);
        res.status(500).json({ message: "Server error" });
    }
});


// UPDATE Profile
app.post("/auth/update", async (req, res) => {
    try {
        if (!req.session.userId) {
            return res.status(401).json({ message: "Not logged in" });
        }

        const { full_name, email, phone, location } = req.body;

        if (!full_name || full_name.trim().length < 2) {
            return res.status(400).json({ message: "Invalid name" });
        }

        await db.query(
            `UPDATE users 
             SET full_name = ?, email = ?, phone = ?, location = ?
             WHERE id = ?`,
            [full_name, email, phone, location, req.session.userId]
        );

        res.json({ message: "Profile updated successfully" });

    } catch (err) {
        console.log(err);
        res.status(500).json({ message: "Server error" });
    }
});






// -----------------------------
// Reports API (requires isAuth)
// -----------------------------

// Create Group Report
app.post('/reports/group', isAuth, async (req, res) => {
  try {
    const { mission, report_date, group_total_exposed, comments } = req.body;

    // basic validation
    if (!mission || !report_date) {
      return res.status(400).json({ message: 'Mission and report_date are required' });
    }

    const [result] = await db.query(
      `INSERT INTO group_reports (mission, report_date, group_total_exposed, comments, created_by)
       VALUES (?, ?, ?, ?, ?)`,
      [mission, report_date, group_total_exposed || 0, comments || null, req.session.userId]
    );

    res.status(201).json({ message: 'Group report saved', id: result.insertId });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});

// List Group Reports (can be filtered by user or all)
app.get('/reports/group', isAuth, async (req, res) => {
  try {
    // optional ?mine=1 to fetch only current user's reports
    const mine = req.query.mine === '1';
    const params = [];
    let sql = `SELECT id, mission, report_date, group_total_exposed, comments, created_by, created_at
               FROM group_reports`;

    if (mine) {
      sql += ` WHERE created_by = ?`;
      params.push(req.session.userId);
    }

    sql += ` ORDER BY created_at DESC LIMIT 200`;
    const [rows] = await db.query(sql, params);
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});

// Create Individual Report
app.post('/reports/individual', isAuth, async (req, res) => {
  try {
    const { full_name, phone, kebele, nearest_church, status, note } = req.body;

    if (!full_name) {
      return res.status(400).json({ message: 'full_name is required' });
    }

    const [result] = await db.query(
      `INSERT INTO individual_reports (full_name, phone, kebele, nearest_church, status, note, created_by)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [full_name, phone || null, kebele || null, nearest_church || null, status || 'hope', note || null, req.session.userId]
    );

    res.status(201).json({ message: 'Individual report saved', id: result.insertId });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});

// List Individual Reports
app.get('/reports/individual', isAuth, async (req, res) => {
  try {
    const mine = req.query.mine === '1';
    const params = [];
    let sql = `SELECT id, full_name, phone, kebele, nearest_church, status, note, created_by, created_at
               FROM individual_reports`;

    if (mine) {
      sql += ` WHERE created_by = ?`;
      params.push(req.session.userId);
    }

    sql += ` ORDER BY created_at DESC LIMIT 200`;
    const [rows] = await db.query(sql, params);
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});


































// Middleware: Admin Authentication
function adminAuth(req, res, next) {
  if (!req.session.adminId) {
    return res.redirect("/");
  }
  next();
}

// ----------------------
//  ADMIN LOGIN
// ----------------------
app.post("/adminlogin", async (req, res) => {
  try {
    const { email, password } = req.body;

    const [rows] = await db.query("SELECT * FROM admins WHERE email = ?", [email]);

    if (rows.length === 0) {
      return res.json({ success: false, message: "Invalid email or password" });
    }

    const admin = rows[0];

    const passwordMatch = await bcrypt.compare(password, admin.password);

    if (!passwordMatch) {
      return res.json({ success: false, message: "Incorrect password" });
    }

    // Save session
    req.session.adminId = admin.id;
    req.session.adminName = admin.full_name;

    res.json({ success: true });
  } catch (err) {
    console.error("Login error:", err);
    res.json({ success: false, message: "Server error" });
  }
});

// ----------------------
//  ADMIN DASHBOARD ROUTE
// ----------------------
app.get("/admindashboard", adminAuth, (req, res) => {
 res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

// ----------------------
//  LOGOUT
// ----------------------
app.get("/adminlogout", (req, res) => {
  req.session.destroy(() => {
    res.redirect("/");
  });
});





app.get("/api/admin-info", adminAuth, async (req, res) => {
    try {
        const [rows] = await db.query("SELECT full_name, role, profile_image, notifications FROM admins WHERE id = ?", [req.session.adminId]);

        if (rows.length === 0) {
            return res.json({ success: false });
        }

        res.json({
            success: true,
            full_name: rows[0].full_name,
            role: rows[0].role,
            profile_image: rows[0].profile_image,
            notifications: rows[0].notifications
        });

    } catch (err) {
        console.error(err);
        res.json({ success: false });
    }
});



app.post('/admin/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) {
            return res.status(500).json({ success: false, message: 'Logout failed' });
        }
        res.clearCookie('gopreach_session');
        res.json({ success: true, message: 'Logged out successfully' });
    });
});




// Add a new member
app.post('/members/add', async (req, res) => {
    try {
        const {
            first_name,
            last_name,
            email,
            phone,
            address,
            role,
            skills,
            experience,
            availability,
            emergency_contact_name,
            emergency_contact_phone
        } = req.body;

        // Validation
        if (!first_name || !last_name || !email) {
            return res.status(400).json({ success: false, message: 'First name, last name, and email are required' });
        }

        const [existing] = await db.query('SELECT * FROM members WHERE email = ?', [email]);
        if (existing.length > 0) {
            return res.status(400).json({ success: false, message: 'Email already exists' });
        }

        const [result] = await db.query(
            `INSERT INTO members 
            (first_name, last_name, email, phone, address, role, skills, experience, availability, emergency_contact_name, emergency_contact_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            [
                first_name,
                last_name,
                email,
                phone,
                address,
                role,
                skills,
                experience,
                availability ? availability.join(',') : null, // store as CSV
                emergency_contact_name,
                emergency_contact_phone
            ]
        );

        res.json({ success: true, message: 'Member added successfully', memberId: result.insertId });

    } catch (err) {
        console.error(err);
        res.status(500).json({ success: false, message: 'Server error' });
    }
});






app.get('/api/members', async (req, res) => {
  try {
    const [rows] = await db.query('SELECT * FROM members');
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database query failed' });
  }
});




app.delete('/api/members/:id', async (req, res) => {
  const memberId = req.params.id;

  try {
    const [result] = await db.query('DELETE FROM members WHERE id = ?', [memberId]);
    
    if (result.affectedRows === 0) {
      return res.status(404).json({ message: 'Member not found.' });
    }

    res.json({ message: 'Member deleted successfully.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error.' });
  }
});





app.put('/api/members/:id', async (req, res) => {
  const id = req.params.id;

  const {
    first_name,
    last_name,
    email,
    phone,
    role,
    skills
  } = req.body;

  try {
    const sql = `
      UPDATE members
      SET first_name = ?, last_name = ?, email = ?, phone = ?, role = ?, skills = ?
      WHERE id = ?
    `;

    const values = [
      first_name,
      last_name,
      email,
      phone,
      role,
      skills,
      id
    ];

    await db.query(sql, values);

    res.json({ message: "Member updated successfully" });

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to update member" });
  }
});





// API TO CREATE MISSION
app.post("/api/missions", (req, res) => {
  const { name, description, start_date, end_date, type, priority } = req.body;

  if (!name || !description || !start_date || !end_date || !type || !priority) {
    return res.status(400).json({ error: "All fields are required" });
  }

  const sql = "INSERT INTO missions (name, description, start_date, end_date, type, priority) VALUES (?, ?, ?, ?, ?, ?)";
  db.query(sql, [name, description, start_date, end_date, type, priority], (err, result) => {
    if (err) {
      console.error("Insert error:", err);
      return res.status(500).json({ error: "Database error" });
    }
    res.json({ message: "Mission created successfully!" });
  });
});



app.get('/api/mission-stats', async (req, res) => {
  try {
    const [rows] = await db.query(`
      SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN start_date <= CURDATE() AND end_date >= CURDATE() THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN MONTH(end_date) = MONTH(CURDATE()) AND YEAR(end_date) = YEAR(CURDATE()) THEN 1 ELSE 0 END) AS completed_this_month
      FROM missions
    `);

    const stats = rows[0];

    res.json({
      total: stats.total,
      active: stats.active,
      completed: stats.completed_this_month,
      teamMembers: 0
    });

  } catch (err) {
    console.error("DB ERROR:", err);
    res.status(500).json({ error: "Database query failed" });
  }
});



app.get("/api/missions", async (req, res) => {
  try {
    const [rows] = await db.query("SELECT * FROM missions ORDER BY created_at DESC");
    res.json(rows);
  } catch (err) {
    console.error("Fetch missions error:", err);
    res.status(500).json({ error: "Failed to fetch missions" });
  }
});


















// -----------------------------
// Start server
app.listen(PORT, () => console.log(`GoPreach Backend running on port ${PORT}`));
