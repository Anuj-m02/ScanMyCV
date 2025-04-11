require("dotenv").config();
const express = require("express");
const cors = require("cors");
const nodemailer = require("nodemailer");

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Create email transporter
const transporter = nodemailer.createTransport({
  host: process.env.EMAIL_HOST,
  port: process.env.EMAIL_PORT,
  secure: false, 
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

transporter.verify((error, success) => {
  if (error) {
    console.error("SMTP connection error:", error);
  } else {
    console.log("Email server is ready to send messages");
  }
});

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ status: "ok", message: "Email service is running" });
});

// Send email endpoint
app.post("/send-email", async (req, res) => {
  try {
    const { to, subject, html, candidateId } = req.body;

    if (!to || !subject || !html || !candidateId) {
      return res.status(400).json({
        success: false,
        message: "Missing required fields (to, subject, html, candidateId)",
      });
    }

    console.log(`Attempting to send email to ${to} (Candidate ${candidateId})`);

    // Send mail
    const info = await transporter.sendMail({
      from: process.env.EMAIL_FROM,
      to,
      subject,
      html,
    });

    console.log(
      `Email sent to ${to} (Candidate ${candidateId}): ${info.messageId}`
    );

    return res.json({
      success: true,
      messageId: info.messageId,
      candidateId,
    });
  } catch (error) {
    console.error("Error sending email:", error);
    return res.status(500).json({
      success: false,
      message: error.message,
    });
  }
});

// Send to multiple candidates
app.post("/send-emails", async (req, res) => {
  try {
    const { candidates } = req.body;

    if (!candidates || !Array.isArray(candidates) || candidates.length === 0) {
      return res.status(400).json({
        success: false,
        message: "Missing or invalid candidates array",
      });
    }

    console.log(
      `Received request to send emails to ${candidates.length} candidates`
    );

    const results = [];
    const errors = [];

    // Process emails in sequence
    for (const candidate of candidates) {
      try {
        if (!candidate.email || !candidate.candidateId) {
          console.log(`Missing email or candidateId for candidate:`, candidate);
          errors.push({
            candidateId: candidate.candidateId || "unknown",
            error: "Missing email or candidateId",
          });
          continue;
        }

        console.log(
          `Preparing email for ${candidate.email} (${candidate.candidateId})`
        );

        const subject =
          candidate.subject || "Congratulations! You have been shortlisted";
        const html =
          candidate.html ||
          `
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #4f46e5;">Congratulations ${
              candidate.candidateName || ""
            }!</h2>
            <p>You have been shortlisted for the position of <strong>${
              candidate.jobTitle || "the position"
            }</strong>.</p>
            <p>Your resume scored an impressive ${
              candidate.score || ""
            }% match with our requirements.</p>
            <p>We will be in touch shortly to schedule an interview.</p>
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
              <p style="color: #666;">Best regards,<br>Recruitment Team</p>
            </div>
          </div>
        `;

        // Send mail
        console.log(`Sending email to ${candidate.email}`);
        const info = await transporter.sendMail({
          from: process.env.EMAIL_FROM,
          to: candidate.email,
          subject,
          html,
        });

        console.log(
          `Email sent to ${candidate.email} (${candidate.candidateId}): ${info.messageId}`
        );

        results.push({
          candidateId: candidate.candidateId,
          email: candidate.email,
          success: true,
          messageId: info.messageId,
        });
      } catch (error) {
        console.error(`Error sending email to ${candidate.email}:`, error);
        errors.push({
          candidateId: candidate.candidateId || "unknown",
          email: candidate.email,
          error: error.message,
        });
      }
    }

    return res.json({
      success: true,
      results,
      errors,
      totalSent: results.length,
      totalFailed: errors.length,
    });
  } catch (error) {
    console.error("Error in batch email operation:", error);
    return res.status(500).json({
      success: false,
      message: error.message,
    });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Email service running on port ${port}`);
});
