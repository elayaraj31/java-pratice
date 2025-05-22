package com.example.invoice;

import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.UUID;

import com.itextpdf.io.image.ImageDataFactory;
import com.itextpdf.kernel.colors.ColorConstants;
import com.itextpdf.kernel.colors.DeviceRgb;
import com.itextpdf.kernel.font.PdfFont;
import com.itextpdf.kernel.font.PdfFontFactory;
import com.itextpdf.kernel.geom.PageSize;
import com.itextpdf.kernel.geom.Rectangle;
import com.itextpdf.kernel.pdf.PdfDocument;
import com.itextpdf.kernel.pdf.PdfWriter;
import com.itextpdf.kernel.pdf.canvas.PdfCanvas;
import com.itextpdf.layout.Document;
import com.itextpdf.layout.borders.Border;
import com.itextpdf.layout.borders.SolidBorder;
import com.itextpdf.layout.element.Cell;
import com.itextpdf.layout.element.Image;
import com.itextpdf.layout.element.Paragraph;
import com.itextpdf.layout.element.Table;
import com.itextpdf.layout.properties.TextAlignment;
import com.itextpdf.layout.properties.UnitValue;

public class PDFGenerator {
    public static void main(String[] args) {
        // Declare variables for all dynamic data
        String outputFile = "invoice.pdf";
        String imagePath = "cam_logo_new.png";
        String instituteName = "Payilagam Training Institute";
        String instituteAddress = "No.7, 1st Main Road, Bhel Sakthi Nagar, Vijaya Nagar, Velachery, Chennai, Tamil Nadu, India-600042.";
        String studentName = "Elayaraj c";
        String studentMobile = "7904451167";
        String studentEmail = "Elayaraj31@gmail.com";
        String studentCourse = "Full Stack Java Development";
        int totalFees = 23000;
        int feesPaid = 9700;
        int sgst = 200;
        int cgst = 100;
        int totalPaid = feesPaid + sgst + cgst;
        int pendingFees = totalFees - totalPaid;
        String paidDate = "10-05-2025";
        String collectedBy = "Payilagam Admin";
        String invoiceNumber = "INV-" + UUID.randomUUID().toString().substring(0, 8);
        DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("dd-MM-yyyy");
        LocalDate parsedPaidDate;
        try {
            parsedPaidDate = LocalDate.parse(paidDate, dateFormatter);
        } catch (DateTimeParseException e) {
            System.err.println("Invalid date format for paidDate: " + paidDate + ". Using current date as fallback.");
            parsedPaidDate = LocalDate.now();
        }

        try {
            // Initialize PDF writer and document
            PdfWriter writer = new PdfWriter(outputFile);
            PdfDocument pdf = new PdfDocument(writer);
            pdf.addNewPage();
            Document document = new Document(pdf, PageSize.A4);
            
            // Create canvas with border and watermark
            PdfCanvas canvas = new PdfCanvas(pdf.getFirstPage());
            Rectangle pageSize = pdf.getFirstPage().getPageSize();
            float margin = 20f;
            canvas.setStrokeColor(ColorConstants.BLACK)
                  .setLineWidth(1)
                  .rectangle(
                      pageSize.getLeft() + margin,
                      pageSize.getBottom() + margin,
                      pageSize.getWidth() - 2 * margin,
                      pageSize.getHeight() - 2 * margin
                  )
                  .stroke();
            // Add watermark (positioned lower)
            canvas.saveState();
            canvas.setFillColor(new DeviceRgb(200, 200, 200)); // Light gray
            PdfFont watermarkFont = PdfFontFactory.createFont("Helvetica");
            canvas.setTextRenderingMode(0) // 0 = FILL
                  .setFontAndSize(watermarkFont, 50)
                  .beginText()
                  .setTextMatrix(1, 0.5f, -0.5f, 1, 170, 300) // Lower position (y=300)
                  .showText("Payilagam")
                  .endText();
            canvas.restoreState();

            // Create fonts
            PdfFont regularFont = PdfFontFactory.createFont("Helvetica");
            PdfFont boldFont = PdfFontFactory.createFont("Helvetica-Bold");
            PdfFont italicFont = PdfFontFactory.createFont("Helvetica-Oblique"); // For signature

            // Institute Header with color
            document.add(new Paragraph(instituteName)
                    .setFont(boldFont)
                    .setFontSize(20)
                    .setTextAlignment(TextAlignment.CENTER)
                    .setBackgroundColor(new DeviceRgb(240, 240, 240)) // Light gray background
                    .setMarginBottom(5));
            document.add(new Paragraph("FEES INVOICE")
                    .setFont(boldFont)
                    .setFontSize(20)
                    .setFontColor(new DeviceRgb(0, 51, 102)) // Dark blue
                    .setTextAlignment(TextAlignment.CENTER)
                    .setMarginBottom(10));

            // Logo and Invoice Details
            Table headerTable = new Table(new float[]{1, 1});
            headerTable.setWidth(UnitValue.createPercentValue(100));
            headerTable.setBackgroundColor(new DeviceRgb(240, 240, 240)); // Light gray background
            
            // Logo
            if (imagePath != null) {
                Cell logoCell = new Cell();
                Image image = new Image(ImageDataFactory.create(imagePath));
                image.setWidth(100);
                logoCell.add(image);
                logoCell.setBorder(Border.NO_BORDER);
                headerTable.addCell(logoCell);
            } else {
                headerTable.addCell(new Cell().setBorder(Border.NO_BORDER));
            }

            // Invoice Details
            Cell detailsCell = new Cell()
                .add(new Paragraph("Invoice #: " + invoiceNumber).setFont(regularFont).setFontSize(11));
            detailsCell.setTextAlignment(TextAlignment.RIGHT);
            detailsCell.setBorder(Border.NO_BORDER);
            headerTable.addCell(detailsCell);
            
            document.add(headerTable.setMarginBottom(15)); // Increased spacing
            
            // Institute Address with heading (moved to right)
            Table addressTable = new Table(new float[]{1});
            addressTable.setWidth(UnitValue.createPercentValue(50));
            addressTable.setHorizontalAlignment(com.itextpdf.layout.properties.HorizontalAlignment.RIGHT);
            addressTable.addCell(new Cell()
                .add(new Paragraph("Address").setFont(boldFont).setFontSize(11))
                .add(new Paragraph(instituteAddress).setFont(regularFont).setFontSize(11))
                .setTextAlignment(TextAlignment.RIGHT)
                .setBorder(Border.NO_BORDER));
            document.add(addressTable.setMarginBottom(30)); // Increased spacing

            // Student Information
            Table studentInfoTable = new Table(new float[]{1, 1});
            studentInfoTable.setWidth(UnitValue.createPercentValue(100));
            studentInfoTable.addCell(new Cell()
                .add(new Paragraph("Student Information").setFont(boldFont).setFontSize(11))
                .add(new Paragraph("Name: " + studentName).setFont(boldFont).setFontSize(11))
                .add(new Paragraph("Mobile: " + studentMobile).setFont(boldFont).setFontSize(11))
                .add(new Paragraph("Email: " + studentEmail).setFont(boldFont).setFontSize(11))
                .setBorder(Border.NO_BORDER));
            studentInfoTable.addCell(new Cell()
                .add(new Paragraph("Course Details").setFont(boldFont).setFontSize(11))
                .add(new Paragraph("Course: " + studentCourse).setFont(boldFont).setFontSize(11))
                .add(new Paragraph("Total Fees: ₹" + totalFees).setFont(boldFont).setFontSize(11))
                .setBorder(Border.NO_BORDER));
            document.add(studentInfoTable.setMarginBottom(30)); // Increased spacing

            // Payment Table Title
            document.add(new Paragraph("Payment Details")
                    .setFont(boldFont)
                    .setFontSize(11)
                    .setMarginBottom(5));

            // Payment Table with alternating row colors
            Table paymentTable = new Table(new float[]{1, 1, 1, 1});
            paymentTable.setWidth(UnitValue.createPercentValue(100));
            
            // Headers
            paymentTable.addHeaderCell(new Cell()
                .add(new Paragraph("Fees Paid").setFont(boldFont).setFontSize(11))
                .setTextAlignment(TextAlignment.CENTER)
                .setBorder(new SolidBorder(1))
                .setBackgroundColor(new DeviceRgb(220, 220, 220)) // Light gray
                .setPadding(8));
            paymentTable.addHeaderCell(new Cell()
                .add(new Paragraph("SGST").setFont(boldFont).setFontSize(11))
                .setTextAlignment(TextAlignment.CENTER)
                .setBorder(new SolidBorder(1))
                .setBackgroundColor(new DeviceRgb(220, 220, 220))
                .setPadding(8));
            paymentTable.addHeaderCell(new Cell()
                .add(new Paragraph("CGST").setFont(boldFont).setFontSize(11))
                .setTextAlignment(TextAlignment.CENTER)
                .setBorder(new SolidBorder(1))
                .setBackgroundColor(new DeviceRgb(220, 220, 220))
                .setPadding(8));
            paymentTable.addHeaderCell(new Cell()
                .add(new Paragraph("Total").setFont(boldFont).setFontSize(11))
                .setTextAlignment(TextAlignment.CENTER)
                .setBorder(new SolidBorder(1))
                .setBackgroundColor(new DeviceRgb(220, 220, 220))
                .setPadding(8));

            // Data
            paymentTable.addCell(new Cell()
                .add(new Paragraph("₹" + feesPaid).setFont(regularFont).setFontSize(11))
                .setTextAlignment(TextAlignment.CENTER)
                .setBorder(new SolidBorder(1))
                .setBackgroundColor(new DeviceRgb(245, 245, 245)) // Very light gray
                .setPadding(8));
            paymentTable.addCell(new Cell()
                .add(new Paragraph("₹" + sgst).setFont(regularFont).setFontSize(11))
                .setTextAlignment(TextAlignment.CENTER)
                .setBorder(new SolidBorder(1))
                .setBackgroundColor(new DeviceRgb(245, 245, 245))
                .setPadding(8));
            paymentTable.addCell(new Cell()
                .add(new Paragraph("₹" + cgst).setFont(regularFont).setFontSize(11))
                .setTextAlignment(TextAlignment.CENTER)
                .setBorder(new SolidBorder(1))
                .setBackgroundColor(new DeviceRgb(245, 245, 245))
                .setPadding(8));
            paymentTable.addCell(new Cell()
                .add(new Paragraph("₹" + totalPaid).setFont(boldFont).setFontSize(11))
                .setTextAlignment(TextAlignment.CENTER)
                .setBorder(new SolidBorder(1))
                .setBackgroundColor(new DeviceRgb(245, 245, 245))
                .setPadding(8));

            document.add(paymentTable.setMarginBottom(30)); // Increased spacing

            // Summary
            Table summaryTable = new Table(new float[]{1, 1});
            summaryTable.setWidth(UnitValue.createPercentValue(100));
            summaryTable.addCell(new Cell()
                .add(new Paragraph("Pending Fees: ₹" + pendingFees).setFont(regularFont).setFontSize(11))
                .add(new Paragraph("Paid Date: " + paidDate).setFont(regularFont).setFontSize(11))
                .setBorder(Border.NO_BORDER));
            summaryTable.addCell(new Cell()
                .add(new Paragraph("Collected By: " + collectedBy).setFont(regularFont).setFontSize(11))
                .setTextAlignment(TextAlignment.RIGHT)
                .setBorder(Border.NO_BORDER));
            document.add(summaryTable.setMarginBottom(30)); // Increased spacing

            // Authorized Signatory with tick mark at page bottom
            Paragraph signature = new Paragraph("[✓] Authorized Signatory: " + collectedBy)
                .setFont(italicFont)
                .setFontSize(8)
                .setTextAlignment(TextAlignment.CENTER)
                .setFixedPosition(36, 50, PageSize.A4.getWidth() - 72); // Above footer
            document.add(signature);
            
            // Alternative: Use a signature image with tick mark (uncomment if you have a signature.png file)
            Paragraph signatureWithImage = new Paragraph("[✓]").setFont(italicFont).setFontSize(8);
            Image signatureImage = new Image(ImageDataFactory.create("929026-middle.png"));
            signatureImage.setWidth(80);
            signatureWithImage.add(new com.itextpdf.layout.element.Text(" Authorized Signatory: " + collectedBy)
            .setFont(italicFont).setFontSize(8));
            signatureWithImage.setTextAlignment(TextAlignment.CENTER)
            .setFixedPosition(36, 50, PageSize.A4.getWidth() - 72);
            document.add(signatureWithImage);
            

            // Footer
            Paragraph footer = new Paragraph("Contact Us: +91 9876543210 | info@payilagam.com | www.payilagam.com")
                .setFont(regularFont)
                .setFontSize(8)
                .setTextAlignment(TextAlignment.CENTER)
                .setFixedPosition(36, 30, PageSize.A4.getWidth() - 72);
            document.add(footer);

            document.close();
            System.out.println("PDF created successfully at " + outputFile);

        } catch (IOException e) {
            System.err.println("Error creating PDF: " + e.getMessage());
            e.printStackTrace();
        }
    }
}