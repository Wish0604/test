// Example payment module
function processPayment(amount, currency = 'USD') {
  if (typeof amount !== 'number' || amount <= 0) {
    throw new Error('Invalid amount')
  }
  // Simulate processing
  console.log(`Processing payment of ${amount} ${currency}`)
  return { status: 'ok', amount, currency, id: Math.floor(Math.random() * 1e6) }
}

module.exports = { processPayment }

// Quick demo when run directly
if (require.main === module) {
  try {
    const result = processPayment(9.99)
    console.log('Result:', result)
  } catch (err) {
    console.error(err.message)
    process.exit(1)
  }
}
