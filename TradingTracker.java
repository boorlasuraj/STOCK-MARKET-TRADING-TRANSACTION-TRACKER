import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.Random;

public class TradingTracker extends JFrame {

    private TransactionTracker tracker;
    private PortfolioManager portfolio;
    private ArrayList<Trade> allTrades;
    
    private JTextField symbolField;
    private JTextField priceField;
    private JTextField volumeField;
    private JTextArea outputArea;

    private Random random;

    public TradingTracker() {
        tracker = new TransactionTracker();
        portfolio = new PortfolioManager();
        allTrades = new ArrayList<>();
        random = new Random();
        
        setTitle("Stock Market Trading Tracker");
        setSize(600, 500);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null); // Center the window.
        
        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(new EmptyBorder(10, 10, 10, 10));
        add(mainPanel);
        
        JPanel inputPanel = new JPanel(new GridLayout(4, 2, 5, 5));
        inputPanel.setBorder(BorderFactory.createTitledBorder("Trade Details"));
        mainPanel.add(inputPanel, BorderLayout.NORTH);
        
        inputPanel.add(new JLabel("Stock Symbol:"));
        symbolField = new JTextField();
        inputPanel.add(symbolField);
        
        inputPanel.add(new JLabel("Price:"));
        priceField = new JTextField("100"); // Default price.
        inputPanel.add(priceField);
        
        inputPanel.add(new JLabel("Volume:"));
        volumeField = new JTextField("10"); // Default volume.
        inputPanel.add(volumeField);
        
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 10, 0));
        JButton addButton = new JButton("Add Trade");
        JButton updateButton = new JButton("Update Prices");
        JButton viewButton = new JButton("View All Trades");
        buttonPanel.add(addButton);
        buttonPanel.add(updateButton);
        buttonPanel.add(viewButton);
        inputPanel.add(buttonPanel);
        
        inputPanel.add(new JLabel());
        
        outputArea = new JTextArea();
        outputArea.setEditable(false);
        outputArea.setFont(new Font("Arial", Font.PLAIN, 12));
        JScrollPane scrollPane = new JScrollPane(outputArea);
        scrollPane.setBorder(BorderFactory.createTitledBorder("Output"));
        mainPanel.add(scrollPane, BorderLayout.CENTER);
        
        addButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                addTrade();
            }
        });
        
        updateButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                updatePrices();
            }
        });
        
        viewButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                updateDisplay("Viewing all trades:");
            }
        });
    }

    private void addTrade() {
        String symbol = symbolField.getText().trim();
        if (symbol.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please enter a stock symbol.", "Input Error", JOptionPane.ERROR_MESSAGE);
            return;
        }
        double price;
        int volume;
        try {
            price = Double.parseDouble(priceField.getText());
            volume = Integer.parseInt(volumeField.getText());
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Price must be a number and volume must be an integer.", "Input Error", JOptionPane.ERROR_MESSAGE);
            return;
        }
        double timestamp = System.currentTimeMillis() / 1000.0;
        Trade trade = new Trade(timestamp, symbol, price, volume);
        tracker.addTrade(trade);
        portfolio.addTrade(trade);
        allTrades.add(trade);
        symbolField.setText("");
        updateDisplay("Trade added: " + trade);
    }

    private double simulatePriceUpdate(Trade trade, double maxFluctuation) {
        double factor = 1 + (random.nextDouble() * 2 * maxFluctuation - maxFluctuation);
        return trade.getPrice() * factor;
    }

    private void updatePrices() {
        for (Trade trade : allTrades) {
            double newPrice = simulatePriceUpdate(trade, 0.05);
            trade.setPrice(newPrice);
        }
        tracker = new TransactionTracker();
        portfolio = new PortfolioManager();
        for (Trade trade : allTrades) {
            tracker.addTrade(trade);
            portfolio.addTrade(trade);
        }
        updateDisplay("Prices updated for all trades.");
    }

    private void updateDisplay(String message) {
        outputArea.setText(""); 
        if (!message.isEmpty()) {
            outputArea.append(message + "\n\n");
        }
        Trade best = tracker.getBestTrade();
        Trade worst = tracker.getWorstTrade();
        if (best != null) {
            outputArea.append("Best Trade: " + best.getSymbol() + " | Profit: " + String.format("%.2f", best.performanceMetric()) + "\n");
        } else {
            outputArea.append("Best Trade: N/A\n");
        }
        if (worst != null) {
            outputArea.append("Worst Trade: " + worst.getSymbol() + " | Profit: " + String.format("%.2f", worst.performanceMetric()) + "\n");
        } else {
            outputArea.append("Worst Trade: N/A\n");
        }
        outputArea.append("\nPortfolio (Inorder Traversal):\n");
        for (Trade trade : portfolio.getInorder()) {
            outputArea.append(trade + " | Performance: " + String.format("%.2f", trade.performanceMetric()) + "\n");
        }
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                TradingTracker trackerApp = new TradingTracker();
                trackerApp.setVisible(true);
            }
        });
    }
}



class Trade {
    private double timestamp;   
    private String symbol;      
    private double price;       
    private int volume;         

    public Trade(double timestamp, String symbol, double price, int volume) {
        this.timestamp = timestamp;
        this.symbol = symbol;
        this.price = price;
        this.volume = volume;
    }

    public double performanceMetric() {
        return price * volume;
    }

    public double getTimestamp() {
        return timestamp;
    }

    public String getSymbol() {
        return symbol;
    }

    public double getPrice() {
        return price;
    }

    public void setPrice(double price) {
        this.price = price;
    }

    public int getVolume() {
        return volume;
    }

    @Override
    public String toString() {
        return "Trade(Symbol: " + symbol +
               ", Price: " + String.format("%.2f", price) +
               ", Volume: " + volume +
               ", Time: " + String.format("%.2f", timestamp) + ")";
    }
}



class TransactionTracker {
    private ArrayList<Trade> trades;

    public TransactionTracker() {
        trades = new ArrayList<>();
    }

    public void addTrade(Trade trade) {
        trades.add(trade);
    }

    public Trade getBestTrade() {
        if (trades.isEmpty()) return null;
        Trade best = trades.get(0);
        for (Trade trade : trades) {
            if (trade.performanceMetric() > best.performanceMetric()) {
                best = trade;
            }
        }
        return best;
    }

    public Trade getWorstTrade() {
        if (trades.isEmpty()) return null;
        Trade worst = trades.get(0);
        for (Trade trade : trades) {
            if (trade.performanceMetric() < worst.performanceMetric()) {
                worst = trade;
            }
        }
        return worst;
    }
}



class AVLNode {
    double key;           
    Trade trade;          
    int height;           
    AVLNode left;         
    AVLNode right;        

    public AVLNode(double key, Trade trade) {
        this.key = key;
        this.trade = trade;
        this.height = 1; 
    }
}



class PortfolioManager {
    private AVLNode root;

    public PortfolioManager() {
        root = null;
    }

    private int getHeight(AVLNode node) {
        return (node == null) ? 0 : node.height;
    }

    private int getBalance(AVLNode node) {
        return (node == null) ? 0 : getHeight(node.left) - getHeight(node.right);
    }

    private AVLNode rightRotate(AVLNode y) {
        AVLNode x = y.left;
        AVLNode T2 = x.right;
        x.right = y;
        y.left = T2;
        y.height = 1 + Math.max(getHeight(y.left), getHeight(y.right));
        x.height = 1 + Math.max(getHeight(x.left), getHeight(x.right));
        return x;
    }

    private AVLNode leftRotate(AVLNode x) {
        AVLNode y = x.right;
        AVLNode T2 = y.left;
        y.left = x;
        x.right = T2;
        x.height = 1 + Math.max(getHeight(x.left), getHeight(x.right));
        y.height = 1 + Math.max(getHeight(y.left), getHeight(y.right));
        return y;
    }

    private AVLNode insertNode(AVLNode node, double key, Trade trade) {
        if (node == null) {
            return new AVLNode(key, trade);
        }
        if (key < node.key) {
            node.left = insertNode(node.left, key, trade);
        } else {
            node.right = insertNode(node.right, key, trade);
        }
        node.height = 1 + Math.max(getHeight(node.left), getHeight(node.right));
        int balance = getBalance(node);
        // Left Left Case
        if (balance > 1 && key < node.left.key) {
            return rightRotate(node);
        }
        // Right Right Case
        if (balance < -1 && key > node.right.key) {
            return leftRotate(node);
        }
        // Left Right Case
        if (balance > 1 && key > node.left.key) {
            node.left = leftRotate(node.left);
            return rightRotate(node);
        }
        // Right Left Case
        if (balance < -1 && key < node.right.key) {
            node.right = rightRotate(node.right);
            return leftRotate(node);
        }
        return node;
    }

    public void addTrade(Trade trade) {
        root = insertNode(root, trade.getTimestamp(), trade);
    }

    private void inorderTraversal(AVLNode node, ArrayList<Trade> result) {
        if (node != null) {
            inorderTraversal(node.left, result);
            result.add(node.trade);
            inorderTraversal(node.right, result);
        }
    }

    public ArrayList<Trade> getInorder() {
        ArrayList<Trade> result = new ArrayList<>();
        inorderTraversal(root, result);
        return result;
    }
}
    