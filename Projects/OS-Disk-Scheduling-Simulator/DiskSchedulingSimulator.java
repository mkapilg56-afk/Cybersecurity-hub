
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.util.*;
import java.util.List;

public class DiskSchedulingSimulator extends JFrame {

    private JTextField requestsField, headField, diskField;
    private JComboBox<String> algorithmBox;
    private JTextArea resultArea;
    private JLabel movementLabel;
    private GraphPanel graphPanel;

    private static class Result {
        List<Integer> path = new ArrayList<>();
        int totalMovement;
    }

    public DiskSchedulingSimulator() {
        setTitle("OS Disk Scheduling Simulator");
        setSize(1100, 720);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout(12, 12));

        getContentPane().setBackground(new Color(240, 243, 248));

        add(createHeader(), BorderLayout.NORTH);
        add(createMainPanel(), BorderLayout.CENTER);
        add(createFooter(), BorderLayout.SOUTH);
    }

    private JPanel createHeader() {
        JPanel header = new JPanel(new BorderLayout());
        header.setBackground(new Color(25, 38, 65));
        header.setBorder(new EmptyBorder(20, 25, 20, 25));

        JLabel title = new JLabel("DISK SCHEDULING SIMULATOR");
        title.setFont(new Font("Arial", Font.BOLD, 25));
        title.setForeground(Color.WHITE);

        JLabel subtitle = new JLabel(
            "Operating Systems | Disk Head Movement Analysis"
        );
        subtitle.setFont(new Font("Arial", Font.PLAIN, 13));
        subtitle.setForeground(new Color(190, 205, 225));

        JPanel textPanel = new JPanel(new GridLayout(2, 1, 0, 5));
        textPanel.setOpaque(false);
        textPanel.add(title);
        textPanel.add(subtitle);

        header.add(textPanel, BorderLayout.WEST);
        return header;
    }

    private JPanel createMainPanel() {
        JPanel main = new JPanel(new BorderLayout(12, 12));
        main.setBackground(new Color(240, 243, 248));
        main.setBorder(new EmptyBorder(15, 18, 10, 18));

        JPanel inputPanel = createInputPanel();

        graphPanel = new GraphPanel();
        graphPanel.setBorder(BorderFactory.createTitledBorder(
            BorderFactory.createLineBorder(new Color(210, 218, 230)),
            "Disk Head Movement Graph",
            TitledBorder.LEFT,
            TitledBorder.TOP,
            new Font("Arial", Font.BOLD, 14)
        ));

        resultArea = new JTextArea();
        resultArea.setEditable(false);
        resultArea.setFont(new Font("Consolas", Font.PLAIN, 14));
        resultArea.setBackground(Color.WHITE);
        resultArea.setMargin(new Insets(12, 12, 12, 12));

        JScrollPane resultScroll = new JScrollPane(resultArea);
        resultScroll.setBorder(BorderFactory.createTitledBorder(
            "Execution Details"
        ));

        movementLabel = new JLabel("Total Head Movement: --");
        movementLabel.setFont(new Font("Arial", Font.BOLD, 17));
        movementLabel.setForeground(new Color(20, 110, 80));

        JPanel rightPanel = new JPanel(new BorderLayout(8, 8));
        rightPanel.setBackground(new Color(240, 243, 248));
        rightPanel.add(graphPanel, BorderLayout.CENTER);
        rightPanel.add(resultScroll, BorderLayout.SOUTH);
        rightPanel.add(movementLabel, BorderLayout.NORTH);

        rightPanel.setPreferredSize(new Dimension(700, 480));

        main.add(inputPanel, BorderLayout.WEST);
        main.add(rightPanel, BorderLayout.CENTER);

        return main;
    }

    private JPanel createInputPanel() {
        JPanel panel = new JPanel(new GridBagLayout());
        panel.setPreferredSize(new Dimension(290, 400));
        panel.setBackground(Color.WHITE);
        panel.setBorder(new CompoundBorder(
            new LineBorder(new Color(210, 218, 230)),
            new EmptyBorder(15, 15, 15, 15)
        ));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0;
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.weightx = 1;
        gbc.insets = new Insets(8, 3, 8, 3);

        JLabel heading = new JLabel("INPUT CONFIGURATION");
        heading.setFont(new Font("Arial", Font.BOLD, 16));
        heading.setForeground(new Color(25, 38, 65));

        gbc.gridy = 0;
        panel.add(heading, gbc);

        requestsField = new JTextField("98, 183, 37, 122, 14, 124, 65, 67");
        headField = new JTextField("53");
        diskField = new JTextField("200");

        addField(panel, gbc, 1, "Disk Requests", requestsField);
        addField(panel, gbc, 3, "Initial Head Position", headField);
        addField(panel, gbc, 5, "Disk Size (Cylinders)", diskField);

        gbc.gridy = 7;
        JLabel algorithmLabel = new JLabel("Select Algorithm");
        algorithmLabel.setFont(new Font("Arial", Font.BOLD, 13));
        panel.add(algorithmLabel, gbc);

        algorithmBox = new JComboBox<>(
            new String[]{"FCFS", "SCAN", "C-SCAN"}
        );
        algorithmBox.setFont(new Font("Arial", Font.PLAIN, 14));

        gbc.gridy = 8;
        panel.add(algorithmBox, gbc);

        JButton runButton = new JButton("RUN SIMULATION");
        runButton.setBackground(new Color(35, 105, 190));
        runButton.setForeground(Color.WHITE);
        runButton.setFocusPainted(false);
        runButton.setFont(new Font("Arial", Font.BOLD, 14));
        runButton.setPreferredSize(new Dimension(220, 42));
        runButton.addActionListener(e -> runSimulation());

        gbc.gridy = 9;
        gbc.insets = new Insets(20, 3, 8, 3);
        panel.add(runButton, gbc);

        JButton clearButton = new JButton("CLEAR RESULTS");
        clearButton.setFont(new Font("Arial", Font.BOLD, 13));
        clearButton.addActionListener(e -> clearResults());

        gbc.gridy = 10;
        gbc.insets = new Insets(8, 3, 8, 3);
        panel.add(clearButton, gbc);

        JLabel note = new JLabel(
            "<html><i>Enter cylinder numbers<br>separated by commas.</i></html>"
        );
        note.setForeground(Color.GRAY);
        note.setFont(new Font("Arial", Font.PLAIN, 12));

        gbc.gridy = 11;
        panel.add(note, gbc);

        return panel;
    }

    private void addField(JPanel panel, GridBagConstraints gbc,
                          int row, String label, JTextField field) {

        gbc.gridy = row;
        JLabel jLabel = new JLabel(label);
        jLabel.setFont(new Font("Arial", Font.BOLD, 13));
        panel.add(jLabel, gbc);

        field.setFont(new Font("Arial", Font.PLAIN, 14));

        gbc.gridy = row + 1;
        panel.add(field, gbc);
    }

    private void runSimulation() {
        try {
            String input = requestsField.getText().trim();

            if (input.isEmpty()) {
                throw new IllegalArgumentException(
                    "Enter at least one disk request."
                );
            }

            String[] values = input.split("[,\\s]+");

            if (values.length > 20) {
                throw new IllegalArgumentException(
                    "Maximum 20 disk requests are allowed."
                );
            }

            int[] requests = new int[values.length];

            for (int i = 0; i < values.length; i++) {
                requests[i] = Integer.parseInt(values[i]);
            }

            int head = Integer.parseInt(headField.getText().trim());
            int disk = Integer.parseInt(diskField.getText().trim());

            if (disk <= 0) {
                throw new IllegalArgumentException(
                    "Disk size must be positive."
                );
            }

            if (head < 0 || head >= disk) {
                throw new IllegalArgumentException(
                    "Initial head must be between 0 and " + (disk - 1)
                );
            }

            for (int request : requests) {
                if (request < 0 || request >= disk) {
                    throw new IllegalArgumentException(
                        "Invalid request: " + request +
                        ". Valid range: 0 to " + (disk - 1)
                    );
                }
            }

            String algorithm = (String) algorithmBox.getSelectedItem();

            Result result = calculate(
                requests, head, disk, algorithm
            );

            displayResult(result, algorithm);

            graphPanel.setData(result.path, disk);

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(
                this,
                "Please enter valid integer values.",
                "Input Error",
                JOptionPane.ERROR_MESSAGE
            );
        } catch (IllegalArgumentException ex) {
            JOptionPane.showMessageDialog(
                this,
                ex.getMessage(),
                "Input Error",
                JOptionPane.ERROR_MESSAGE
            );
        }
    }

    private Result calculate(int[] requests, int head,
                             int disk, String algorithm) {

        Result result = new Result();

        result.path.add(head);

        int[] sorted = requests.clone();
        Arrays.sort(sorted);

        int position = head;

        if (algorithm.equals("FCFS")) {

            for (int request : requests) {
                result.path.add(request);
            }

        } else if (algorithm.equals("SCAN")) {

            for (int request : sorted) {
                if (request >= head) {
                    result.path.add(request);
                }
            }

            result.path.add(disk - 1);

            for (int i = sorted.length - 1; i >= 0; i--) {
                if (sorted[i] < head) {
                    result.path.add(sorted[i]);
                }
            }

        } else if (algorithm.equals("C-SCAN")) {

            for (int request : sorted) {
                if (request >= head) {
                    result.path.add(request);
                }
            }

            result.path.add(disk - 1);
            result.path.add(0);

            for (int request : sorted) {
                if (request < head) {
                    result.path.add(request);
                }
            }
        }

        for (int i = 1; i < result.path.size(); i++) {
            result.totalMovement += Math.abs(
                result.path.get(i) - result.path.get(i - 1)
            );
        }

        return result;
    }

    private void displayResult(Result result, String algorithm) {

        StringBuilder output = new StringBuilder();

        output.append("Algorithm: ").append(algorithm).append("\n\n");

        output.append("Head Movement Sequence:\n");

        for (int i = 0; i < result.path.size(); i++) {
            output.append(result.path.get(i));

            if (i < result.path.size() - 1) {
                output.append("  ->  ");
            }
        }

        output.append("\n\nIndividual Movements:\n");

        for (int i = 1; i < result.path.size(); i++) {
            int from = result.path.get(i - 1);
            int to = result.path.get(i);

            output.append(from)
                  .append(" -> ")
                  .append(to)
                  .append(" = ")
                  .append(Math.abs(to - from))
                  .append(" cylinders\n");
        }

        output.append("\nTotal Head Movement = ")
              .append(result.totalMovement)
              .append(" cylinders");

        resultArea.setText(output.toString());

        movementLabel.setText(
            "Total Head Movement: " +
            result.totalMovement + " cylinders"
        );
    }

    private void clearResults() {
        resultArea.setText("");
        movementLabel.setText("Total Head Movement: --");
        graphPanel.setData(new ArrayList<>(), 200);
    }

    private JPanel createFooter() {
        JPanel footer = new JPanel();
        footer.setBackground(new Color(25, 38, 65));
        footer.setBorder(new EmptyBorder(10, 5, 10, 5));

        JLabel label = new JLabel(
            "OS Mini Project | Disk Scheduling Simulator | Java Swing"
        );
        label.setForeground(Color.WHITE);
        label.setFont(new Font("Arial", Font.PLAIN, 12));

        footer.add(label);
        return footer;
    }

    // Graph visualization using Java Swing

    private static class GraphPanel extends JPanel {

        private List<Integer> path = new ArrayList<>();
        private int diskSize = 200;

        public GraphPanel() {
            setBackground(Color.WHITE);
            setPreferredSize(new Dimension(650, 350));
        }

        public void setData(List<Integer> path, int diskSize) {
            this.path = new ArrayList<>(path);
            this.diskSize = diskSize;
            repaint();
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);

            Graphics2D g2 = (Graphics2D) g.create();

            g2.setRenderingHint(
                RenderingHints.KEY_ANTIALIASING,
                RenderingHints.VALUE_ANTIALIAS_ON
            );

            int width = getWidth();
            int height = getHeight();

            int left = 65;
            int right = 25;
            int top = 35;
            int bottom = 55;

            int graphWidth = width - left - right;
            int graphHeight = height - top - bottom;

            g2.setColor(Color.DARK_GRAY);
            g2.setFont(new Font("Arial", Font.BOLD, 12));

            g2.drawString("Cylinder", 10, 20);
            g2.drawString("Movement Step", width / 2 - 45, height - 10);

            if (path.size() < 2 || diskSize <= 0) {
                g2.setColor(Color.GRAY);
                g2.drawString(
                    "Run a simulation to display the graph.",
                    width / 2 - 125,
                    height / 2
                );
                g2.dispose();
                return;
            }

            int maxCylinder = diskSize - 1;
            int steps = path.size() - 1;

            // Draw grid and cylinder labels

            g2.setFont(new Font("Arial", Font.PLAIN, 10));

            for (int i = 0; i <= 5; i++) {
                int y = top + graphHeight * i / 5;
                int cylinder = maxCylinder -
                    (int) ((long) maxCylinder * i / 5);

                g2.setColor(new Color(225, 230, 238));
                g2.drawLine(left, y, width - right, y);

                g2.setColor(Color.DARK_GRAY);
                g2.drawString(String.valueOf(cylinder), 20, y + 4);
            }

            // Draw movement lines

            g2.setStroke(new BasicStroke(2.5f));
            g2.setColor(new Color(35, 105, 190));

            for (int i = 0; i < path.size() - 1; i++) {

                int x1 = left + graphWidth * i / steps;
                int x2 = left + graphWidth * (i + 1) / steps;

                int y1 = top + graphHeight -
                    (int) ((long) path.get(i) * graphHeight / maxCylinder);

                int y2 = top + graphHeight -
                    (int) ((long) path.get(i + 1) * graphHeight / maxCylinder);

                g2.drawLine(x1, y1, x2, y2);
            }

            // Draw points and cylinder values

            for (int i = 0; i < path.size(); i++) {

                int x = left + graphWidth * i / steps;

                int y = top + graphHeight -
                    (int) ((long) path.get(i) * graphHeight / maxCylinder);

                g2.setColor(new Color(220, 70, 70));
                g2.fillOval(x - 5, y - 5, 10, 10);

                g2.setColor(Color.DARK_GRAY);
                g2.setFont(new Font("Arial", Font.BOLD, 10));
                g2.drawString(
                    String.valueOf(path.get(i)),
                    x - 10,
                    y - 10
                );

                g2.setFont(new Font("Arial", Font.PLAIN, 10));
                g2.drawString(
                    String.valueOf(i),
                    x - 3,
                    top + graphHeight + 18
                );
            }

            g2.dispose();
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            DiskSchedulingSimulator app =
                new DiskSchedulingSimulator();

            app.setVisible(true);
        });
    }
}
