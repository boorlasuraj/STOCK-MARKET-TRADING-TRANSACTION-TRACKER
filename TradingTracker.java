import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.table.AbstractTableModel;
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
    private JTable tradeTable;
    private TradeTableModel tableModel;
    private JLabel bestTradeLabel;
    private JLabel worstTradeLabel;

    private Random random;
    private javax.swing.Timer priceUpdateTimer;

    public TradingTracker() {
        tracker = new TransactionTracker();
        portfolio = new PortfolioManager();
        allTrades = new ArrayList<>();
        random = new Random();

        setTitle("Stock Market Trading Tracker");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null); // Center the window.

        // Main container - BorderLayout.
        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(new EmptyBorder(10, 10, 10, 10));
        add(mainPanel);

        // Top 
        JPanel topPanel = new JPanel();
        topPanel.setLayout(new BoxLayout(topPanel, BoxLayout.Y_AXIS));
        mainPanel.add(topPanel, BorderLayout.NORTH);

        // Trade details panel  - GridLayout.
        JPanel detailsPanel = new JPanel(new GridLayout(1, 6, 5, 5));
        detailsPanel.setBorder(BorderFactory.createTitledBorder("Trade Details"));
        topPanel.add(detailsPanel);

        detailsPanel.add(new JLabel("Stock Symbol:"));
        symbolField = new JTextField();
        detailsPanel.add(symbolField);

        detailsPanel.add(new JLabel("Price:"));
        priceField = new JTextField("100");
        detailsPanel.add(priceField);

        detailsPanel.add(new JLabel("Volume:"));
        volumeField = new JTextField("10");
        detailsPanel.add(volumeField);

        // Buttons panel- FlowLayout centered.
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 15, 5));
        topPanel.add(buttonPanel);
        buttonPanel.setBorder(BorderFactory.createEmptyBorder(5, 0, 5, 0));

        JButton addButton = new JButton("Add Trade");
        JButton sellButton = new JButton("Sell Stock");
        JButton updateAllButton = new JButton("Update All Prices");
        JButton updateSelectedButton = new JButton("Update Selected Stock");
        buttonPanel.add(addButton);
        buttonPanel.add(sellButton);
        buttonPanel.add(updateAllButton);
        buttonPanel.add(updateSelectedButton);

        //   table 
        tableModel = new TradeTableModel(allTrades);
        tradeTable = new JTable(tableModel);
        JScrollPane tableScroll = new JScrollPane(tradeTable);
        tableScroll.setBorder(BorderFactory.createTitledBorder("Trades"));
        mainPanel.add(tableScroll, BorderLayout.CENTER);

        // Summary 
        JPanel summaryPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 5));
        bestTradeLabel = new JLabel("Best Trade: N/A");
        worstTradeLabel = new JLabel("Worst Trade: N/A");
        summaryPanel.add(bestTradeLabel);
        summaryPanel.add(worstTradeLabel);
        mainPanel.add(summaryPanel, BorderLayout.SOUTH);

        // Button action
        addButton.addActionListener(e -> addTrade());
        sellButton.addActionListener(e -> sellTrade());
        updateAllButton.addActionListener(e -> updateAllPrices());
        updateSelectedButton.addActionListener(e -> updateSelectedStock());

        //  Swing Timer - 10 seconds.
        priceUpdateTimer = new javax.swing.Timer(10000, e -> updateAllPrices());
        priceUpdateTimer.start();

        updateSummary();
    }

    // Buy
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
        Trade trade = new Trade(timestamp, symbol, price, volume, price, "Buy");
        tracker.addTrade(trade);
        portfolio.addTrade(trade);
        allTrades.add(trade);
        symbolField.setText("");
        tableModel.fireTableDataChanged();
        updateSummary();
    }

    // Sell 
    private void sellTrade() {
        String symbol = JOptionPane.showInputDialog(this, "Enter the stock symbol to sell:");
        if (symbol == null || symbol.trim().isEmpty()) {
            return;
        }
        Trade buyTrade = null;
        for (Trade t : allTrades) {
            if (t.getSymbol().equalsIgnoreCase(symbol.trim()) && t.getTradeType().equals("Buy") && t.getVolume() > 0) {
                buyTrade = t;
                break;
            }
        }
        if (buyTrade == null) {
            JOptionPane.showMessageDialog(this, "No available buy trade found for symbol: " + symbol, "Sell Error", JOptionPane.ERROR_MESSAGE);
            return;
        }
        String volStr = JOptionPane.showInputDialog(this, "Enter number of shares to sell (Available: " + buyTrade.getVolume() + "):");
        if (volStr == null || volStr.trim().isEmpty()) {
            return;
        }
        int sellVolume;
        try {
            sellVolume = Integer.parseInt(volStr);
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Volume must be an integer.", "Input Error", JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (sellVolume <= 0 || sellVolume > buyTrade.getVolume()) {
            JOptionPane.showMessageDialog(this, "Invalid sell volume. Must be between 1 and " + buyTrade.getVolume(), "Sell Error", JOptionPane.ERROR_MESSAGE);
            return;
        }
        double currentPrice = buyTrade.getPrice();
        double timestamp = System.currentTimeMillis() / 1000.0;
        Trade sellTrade = new Trade(timestamp, symbol, currentPrice, sellVolume, buyTrade.getOriginalPrice(), "Sell");
        tracker.addTrade(sellTrade);
        portfolio.addTrade(sellTrade);
        allTrades.add(sellTrade);
        buyTrade.reduceVolume(sellVolume);
        tableModel.fireTableDataChanged();
        updateSummary();
    }

    // price update.
    private double simulatePriceUpdate(Trade trade, double maxFluctuation) {
        double factor = 1 + (random.nextDouble() * 2 * maxFluctuation - maxFluctuation);
        return trade.getPrice() * factor;
    }

    // Update all 
    private void updateAllPrices() {
        for (Trade trade : allTrades) {
            if (trade.getTradeType().equals("Buy") && trade.getVolume() > 0) {
                double newPrice = simulatePriceUpdate(trade, 0.05);
                trade.setPrice(newPrice);
            }
        }
        tracker = new TransactionTracker();
        portfolio = new PortfolioManager();
        for (Trade trade : allTrades) {
            tracker.addTrade(trade);
            portfolio.addTrade(trade);
        }
        tableModel.fireTableDataChanged();
        updateSummary();
    }

    // Update for selected trade.
    private void updateSelectedStock() {
        int selectedRow = tradeTable.getSelectedRow();
        if (selectedRow == -1) {
            JOptionPane.showMessageDialog(this, "Please select a trade to update.", "No Selection", JOptionPane.WARNING_MESSAGE);
            return;
        }
        Trade trade = allTrades.get(selectedRow);
        if (!trade.getTradeType().equals("Buy") || trade.getVolume() <= 0) {
            JOptionPane.showMessageDialog(this, "Selected trade is not an active buy trade.", "Update Error", JOptionPane.ERROR_MESSAGE);
            return;
        }
        double newPrice = simulatePriceUpdate(trade, 0.05);
        trade.setPrice(newPrice);
        tracker = new TransactionTracker();
        portfolio = new PortfolioManager();
        for (Trade t : allTrades) {
            tracker.addTrade(t);
            portfolio.addTrade(t);
        }
        tableModel.fireTableDataChanged();
        updateSummary();
    }

    // Update best and worst trade 
    private void updateSummary() {
        Trade best = tracker.getBestTrade();
        Trade worst = tracker.getWorstTrade();
        bestTradeLabel.setText(best != null ? "Best Trade: " + best.getSymbol() + " | Profit: " + String.format("%.2f", best.performanceMetric()) : "Best Trade: N/A");
        worstTradeLabel.setText(worst != null ? "Worst Trade: " + worst.getSymbol() + " | Profit: " + String.format("%.2f", worst.performanceMetric()) : "Worst Trade: N/A");
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            TradingTracker trackerApp = new TradingTracker();
            trackerApp.setVisible(true);
        });
    }
}

// Table model to display trades
class TradeTableModel extends AbstractTableModel {

    private final String[] columnNames = {"Timestamp", "Symbol", "Type", "Price", "Volume", "Orig. Price", "Performance"};
    private ArrayList<Trade> trades;

    public TradeTableModel(ArrayList<Trade> trades) {
        this.trades = trades;
    }

    @Override
    public int getRowCount() {
        return trades.size();
    }

    @Override
    public int getColumnCount() {
        return columnNames.length;
    }
    
    @Override
    public String getColumnName(int col) {
        return columnNames[col];
    }
    
    @Override
    public Object getValueAt(int row, int col) {
        Trade trade = trades.get(row);
        switch (col) {
            case 0:
                return String.format("%.2f", trade.getTimestamp());
            case 1:
                return trade.getSymbol();
            case 2:
                return trade.getTradeType();
            case 3:
                return String.format("%.2f", trade.getPrice());
            case 4:
                return trade.getVolume();
            case 5:
                return String.format("%.2f", trade.getOriginalPrice());
            case 6:
                return String.format("%.2f", trade.performanceMetric());
            default:
                return "";
        }
    }
}


class Trade {
    private double timestamp;
    private String symbol;
    private double price;
    private int volume;
    private double originalPrice;
    private String tradeType;

    public Trade(double timestamp, String symbol, double price, int volume, double originalPrice, String tradeType) {
        this.timestamp = timestamp;
        this.symbol = symbol;
        this.price = price;
        this.volume = volume;
        this.originalPrice = originalPrice;
        this.tradeType = tradeType;
    }

    public double performanceMetric() {
        return (price - originalPrice) * volume;
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
        if (tradeType.equals("Buy")) {
            this.price = price;
        }
    }

    public int getVolume() {
        return volume;
    }

    public void reduceVolume(int amount) {
        this.volume -= amount;
        if (this.volume < 0) {
            this.volume = 0;
        }
    }

    public double getOriginalPrice() {
        return originalPrice;
    }

    public String getTradeType() {
        return tradeType;
    }

    @Override
    public String toString() {
        return "Trade(Symbol: " + symbol +
               ", Type: " + tradeType +
               ", Price: " + String.format("%.2f", price) +
               ", Volume: " + volume +
               ", Orig.Price: " + String.format("%.2f", originalPrice) +
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
        if (balance > 1 && key < node.left.key) {
            return rightRotate(node);
        }
        if (balance < -1 && key > node.right.key) {
            return leftRotate(node);
        }
        if (balance > 1 && key > node.left.key) {
            node.left = leftRotate(node.left);
            return rightRotate(node);
        }
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


