package com.example.invoice;

import java.io.IOException;

import com.itextpdf.io.image.ImageDataFactory;
import com.itextpdf.kernel.colors.ColorConstants;
import com.itextpdf.kernel.font.PdfFont;
import com.itextpdf.kernel.font.PdfFontFactory;
import com.itextpdf.kernel.geom.PageSize;
import com.itextpdf.kernel.geom.Rectangle;
import com.itextpdf.kernel.pdf.PdfDocument;
import com.itextpdf.kernel.pdf.PdfWriter;
import com.itextpdf.kernel.pdf.canvas.PdfCanvas;
import com.itextpdf.layout.Document;
import com.itextpdf.layout.element.Cell;
import com.itextpdf.layout.element.Image;
import com.itextpdf.layout.element.Paragraph;
import com.itextpdf.layout.element.Table;
import com.itextpdf.layout.properties.TextAlignment;

public class PDFGenerator {
    public static void main(String[] args) {
        // Declare variables for all dynamic data
        String outputFile = "invoice.pdf";
        String imagePath = "cam_logo_new.png"; // Replace with your image path or set to null if no image
        String instituteAddress = "No.7, 1st Main Road, Bhel Sakthi Nagar, Vijaya Nagar, Velechery, Chennai, Tamil Nadu, India-600042.";
        String studentName = "Elayaraj C";
        String studentMobile = "7904451167";
        String studentEmail = "Elayaraj31@gmail.com";
        String studentCourse = "Full Stack Java Development";
        int totalFees = 23000;
        int feesPaid = 9700;
        int sgst = 200;
        int cgst = 100;
        int totalPaid = feesPaid + sgst + cgst; // Calculate total paid
        int pendingFees = totalFees - totalPaid; // Calculate pending fees
        String paidDate = "10-05-2025";
        String collectedBy = "Payilagam Admin";

        try {
        	// Initialize PDF writer and document
        	PdfWriter writer = new PdfWriter(outputFile);
        	PdfDocument pdf = new PdfDocument(writer);

        	// ✅ Add a page before accessing it
        	pdf.addNewPage();
        	Document document = new Document(pdf, PageSize.A4);

        	// Now you can safely create the canvas
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


            // Create fonts
            PdfFont font = PdfFontFactory.createFont();
            PdfFont boldFont = PdfFontFactory.createFont();

            // Header
            Paragraph header = new Paragraph("FEES INVOICE")
                    .setFont(boldFont)
                    .setFontSize(14)
                    .setTextAlignment(TextAlignment.CENTER);
            document.add(header);

            // Image
            if (imagePath != null) {
                Image image = new Image(ImageDataFactory.create(imagePath));
                image.setWidth(200);
                image.setHorizontalAlignment(com.itextpdf.layout.properties.HorizontalAlignment.CENTER);
                document.add(image);
            }


            // Institute Address
            document.add(new Paragraph(instituteAddress)
                    .setFont(font)
                    .setFontSize(12)
                    .setMarginBottom(20)
                    .setTextAlignment(TextAlignment.CENTER)
            );

            // Student Information
            document.add(new Paragraph("Name: " + studentName)
                    .setFont(font)
                    .setFontSize(12));
            document.add(new Paragraph("Mobile: " + studentMobile)
                    .setFont(font)
                    .setFontSize(12));
            document.add(new Paragraph("Email: " + studentEmail)
                    .setFont(font)
                    .setFontSize(12));
            document.add(new Paragraph("Course: " + studentCourse)
                    .setFont(font)
                    .setFontSize(12));
            document.add(new Paragraph("Total Fees: " + totalFees)
                    .setFont(font)
                    .setFontSize(12)
                    .setMarginBottom(5));

            // Create Table
            Table table = new Table(new float[]{100, 150, 100, 100});
            table.setMarginBottom(20);

            // Add table headers (Center Aligned)
            table.addHeaderCell(new Cell().add(new Paragraph("Fees Paid")
                    .setFont(boldFont)
                    .setTextAlignment(TextAlignment.CENTER)));
            table.addHeaderCell(new Cell().add(new Paragraph("SGST")
                    .setFont(boldFont)
                    .setTextAlignment(TextAlignment.CENTER)));
            table.addHeaderCell(new Cell().add(new Paragraph("CGST")
                    .setFont(boldFont)
                    .setTextAlignment(TextAlignment.CENTER)));
            table.addHeaderCell(new Cell().add(new Paragraph("Total")
                    .setFont(boldFont)
                    .setTextAlignment(TextAlignment.CENTER)));

            // Add table rows with variables (Center Aligned)
            table.addCell(new Cell().add(new Paragraph(String.valueOf(feesPaid))
                    .setTextAlignment(TextAlignment.CENTER)));
            table.addCell(new Cell().add(new Paragraph(String.valueOf(sgst))
                    .setTextAlignment(TextAlignment.CENTER)));
            table.addCell(new Cell().add(new Paragraph(String.valueOf(cgst))
                    .setTextAlignment(TextAlignment.CENTER)));
            table.addCell(new Cell().add(new Paragraph(String.valueOf(totalPaid))
                    .setTextAlignment(TextAlignment.CENTER)));

            document.add(table);

            // Pending Fees & Payment Date
            document.add(new Paragraph("Pending Fees: " + pendingFees)
                    .setFont(font)
                    .setFontSize(12));
            document.add(new Paragraph("Paid Date: " + paidDate)
                    .setFont(font)
                    .setFontSize(12));

            // Collected By (Right Aligned)
            document.add(new Paragraph("Collected By")
                    .setFont(font)
                    .setFontSize(12)
                    .setMarginLeft(400));
            document.add(new Paragraph(collectedBy)
                    .setFont(font)
                    .setFontSize(12)
                    .setMarginLeft(400));

            document.close();
            System.out.println("PDF created successfully at " + outputFile);

        } catch (IOException e) {
            System.err.println("Error creating PDF: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
